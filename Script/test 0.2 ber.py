import random

# ==========================================
# CẤU HÌNH CƠ BẢN
# ==========================================
TYPES = ['ATK', 'DEF', 'SPE']
STYLES = {'Light': 7, 'Combo': 9, 'Heavy': 11}

class Card:
    def __init__(self, card_type, style):
        self.type = card_type
        self.style = style
        self.value = STYLES[style]
    def __repr__(self):
        return f"[{self.type}-{self.style}]"

class GameSim:
    def __init__(self):
        self.turn_count = 0
        self.p_hp = 50
        self.p_mot = 50
        self.p_cor = 50
        self.m_hp = 50

        # THIẾT LẬP BỘ BÀI
        self.p_deck = [
            Card('ATK', 'Light'), Card('ATK', 'Combo'), Card('ATK', 'Heavy'), Card('ATK', 'Light'), Card('ATK', 'Combo'),
            Card('DEF', 'Light'), Card('DEF', 'Combo'), Card('DEF', 'Heavy'), Card('DEF', 'Combo'), Card('DEF', 'Light'),
            Card('SPE', 'Light'), Card('SPE', 'Combo'), Card('SPE', 'Heavy'), Card('SPE', 'Light'), Card('SPE', 'Combo')
        ]
        self.p_graveyard = []
        random.shuffle(self.p_deck)

        self.m_deck = [
            Card('ATK', 'Heavy'), Card('ATK', 'Heavy'), Card('ATK', 'Combo'), Card('ATK', 'Combo'), Card('ATK', 'Combo'),
            Card('ATK', 'Light'), Card('ATK', 'Light'), Card('DEF', 'Heavy'), Card('DEF', 'Combo'), Card('DEF', 'Light'),
            Card('SPE', 'Heavy'), Card('SPE', 'Combo'), Card('SPE', 'Light'), Card('ATK', 'Light'), Card('ATK', 'Light')
        ]
        self.m_graveyard = []
        random.shuffle(self.m_deck)

    def draw_cards(self, amount, is_player=True):
        hand = []
        deck = self.p_deck if is_player else self.m_deck
        graveyard = self.p_graveyard if is_player else self.m_graveyard
        
        for _ in range(amount):
            if len(deck) == 0:
                deck.extend(graveyard)
                graveyard.clear()
                random.shuffle(deck)
            if len(deck) > 0:
                hand.append(deck.pop(0))
                
        if is_player:
            self.p_deck, self.p_graveyard = deck, graveyard
        else:
            self.m_deck, self.m_graveyard = deck, graveyard
        return hand

    def apply_effect(self, card, is_player, is_x2=False):
        val = card.value * (2 if is_x2 else 1)
        if card.type == 'ATK':
            if is_player: self.m_hp = max(0, self.m_hp - val)
            else: self.p_hp = max(0, self.p_hp - val)
        elif card.type == 'DEF':
            if card.style == 'Combo':
                if is_player: self.p_hp = min(50, self.p_hp + val)
                else: self.m_hp = min(50, self.m_hp + val) 
            else:
                if is_player: self.p_mot += val
                else: self.p_mot -= val
        elif card.type == 'SPE':
            if card.style == 'Combo':
                if is_player: self.p_hp = min(50, self.p_hp + val)
                else: self.m_hp = min(50, self.m_hp + val)
            else:
                if is_player: self.p_cor -= val
                else: self.p_cor += val

    def clash(self, p_card, m_card):
        # 1. ĐỌ LỚP 2
        if p_card.type == m_card.type:
            if p_card.style == m_card.style: return
            p_wins_sub = (p_card.style == 'Heavy' and m_card.style == 'Combo') or \
                         (p_card.style == 'Combo' and m_card.style == 'Light') or \
                         (p_card.style == 'Light' and m_card.style == 'Heavy')
            if p_wins_sub: self.apply_effect(p_card, True, True)
            else: self.apply_effect(m_card, False, True)
        # 2. ĐỌ LỚP 1
        else:
            p_wins_l1 = (p_card.type == 'DEF' and m_card.type == 'ATK') or \
                        (p_card.type == 'ATK' and m_card.type == 'SPE') or \
                        (p_card.type == 'SPE' and m_card.type == 'DEF')
            if p_wins_l1: self.apply_effect(p_card, True, False)
            else: self.apply_effect(m_card, False, False)

    def auto_choose(self, hand, m_action, state_signal):
        """AI Tự động đưa ra quyết định dựa trên Tín hiệu và Lớp 2"""
        
        # ƯU TIÊN 1a: Quái Cuồng Nộ (100% ATK) -> Cố gắng lấy DEF chặn sát thương
        if state_signal == "CUONG_NO":
            def_cards = [c for c in hand if c.type == 'DEF']
            if def_cards: return def_cards[0]
            
        # ƯU TIÊN 1b: Quái Hoảng Sợ (0% ATK) -> An toàn tuyệt đối, xả ATK để đục máu hoặc ép SPE
        if state_signal == "HOANG_SO":
            atk_cards = [c for c in hand if c.type == 'ATK']
            if atk_cards: return atk_cards[0]
            
        # ƯU TIÊN 2: Bắt bài Lớp 2 (Style) khi tín hiệu không rõ ràng
        counter_style = {'Heavy': 'Light', 'Combo': 'Heavy', 'Light': 'Combo'}[m_action.style]
        l2_counters = [c for c in hand if c.style == counter_style]
        if l2_counters: return l2_counters[0]
        
        # ƯU TIÊN 3: Không có bài bắt bài -> Bốc lá đầu tiên
        return hand[0]

    def run_game(self):
        while True:
            self.turn_count += 1  
            if self.p_hp <= 0: return "PLAYER_DEAD", self.p_hp
            if self.m_hp <= 0: return "MONSTER_DEAD", self.p_hp
            if self.p_mot >= 80 or self.p_mot <= 20 or self.p_cor >= 80 or self.p_cor <= 20: return "STATUS_OOB", self.p_hp

            hand = self.draw_cards(5, True)
            m_hand = self.draw_cards(5, False)
            m_actions = random.sample(m_hand, 3)
            unused_m_cards = [c for c in m_hand if c not in m_actions]

            # Phân tích Tín hiệu
            atk_c = sum(1 for c in m_actions if c.type == 'ATK')
            state_signal = "NORMAL"
            if atk_c == 3: state_signal = "CUONG_NO"
            elif atk_c == 2: state_signal = "NOI_DIEN"
            elif atk_c == 0: state_signal = "HOANG_SO"
            elif atk_c == 1: state_signal = "E_DE" 

            # Người chơi (AI) chọn bài
            p_choices = []
            for i in range(3):
                chosen = self.auto_choose(hand, m_actions[i], state_signal)
                p_choices.append(chosen)
                hand.remove(chosen)
                
            # Va chạm
            for i in range(3):
                self.clash(p_choices[i], m_actions[i])
                if self.p_hp <= 0: return "PLAYER_DEAD", self.p_hp
                if self.m_hp <= 0: return "MONSTER_DEAD", self.p_hp

            if self.p_mot >= 80 or self.p_mot <= 20 or self.p_cor >= 80 or self.p_cor <= 20:
                return "STATUS_OOB", self.p_hp

            self.p_graveyard.extend(p_choices + hand)
            self.m_graveyard.extend(m_actions + unused_m_cards)

# ==========================================
# CHẠY MÔ PHỎNG 1000 LẦN
# ==========================================
def run_simulation(runs=1000):
    results = {"MONSTER_DEAD": 0, "PLAYER_DEAD": 0, "STATUS_OOB": 0}
    total_turns = 0

    total_hp_when_won = 0 # BIẾN MỚI: Tích lũy máu khi thắng
    
    for _ in range(runs):
        game = GameSim()
        # outcome = game.run_game()
        outcome, final_hp = game.run_game() # Nhận cả 2 giá trị trả về
        results[outcome] += 1
        total_turns += game.turn_count

        if outcome == "MONSTER_DEAD":
            total_hp_when_won += final_hp # Cộng dồn máu nếu thắng
    
    print(f"--- KẾT QUẢ MÔ PHỎNG {runs} TRẬN (AI ĐÃ CẬP NHẬT TƯ DUY) ---")
    print(f"Trung bình số Lượt (Turns) / Trận: {total_turns / runs:.2f}")
    print(f"Tỷ lệ Player THẮNG (Quái hết HP): {results['MONSTER_DEAD'] / runs * 100:.1f}%")
    if results['MONSTER_DEAD'] > 0:
        avg_hp = total_hp_when_won / results['MONSTER_DEAD']
        print(f"   -> Lượng HP trung bình còn lại khi thắng: {avg_hp:.1f}/50")
    print(f"Tỷ lệ Player THUA (Hết HP): {results['PLAYER_DEAD'] / runs * 100:.1f}%")
    print(f"Tỷ lệ Vỡ Trạng Thái (MOT/COR): {results['STATUS_OOB'] / runs * 100:.1f}%\n")

if __name__ == "__main__":
    run_simulation(100000)