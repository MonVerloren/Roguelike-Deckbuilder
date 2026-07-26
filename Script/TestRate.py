import random

TYPES = ['ATK', 'DEF', 'SPE']
STYLES = {'Light': 5, 'Combo': 7, 'Heavy': 9} # Thông số cân bằng 5/7/9

class Card:
    def __init__(self, card_type, style):
        self.type = card_type
        self.style = style
        self.value = STYLES[style]

class GameSim:
    def __init__(self):
        self.p_hp = 50
        self.p_mot = 50
        self.p_cor = 50
        self.m_hp = 50
        self.turns = 0
        
        self.p_deck = [Card(t, s) for t in TYPES for s in STYLES.keys()] + [Card('ATK', 'Combo'), Card('DEF', 'Heavy'), Card('SPE', 'Light'), Card('ATK', 'Heavy'), Card('DEF', 'Combo'), Card('SPE', 'Combo')]
        self.p_graveyard = []
        random.shuffle(self.p_deck)

        self.m_deck = [Card('ATK', 'Heavy')] * 5 + [Card('ATK', 'Combo')] * 3 + [Card('DEF', 'Heavy')] * 3 + [Card('SPE', 'Combo')] * 4
        self.m_graveyard = []
        random.shuffle(self.m_deck)

    def draw_cards(self, amount, is_player=True):
        hand = []
        deck = self.p_deck if is_player else self.m_deck
        graveyard = self.p_graveyard if is_player else self.m_graveyard
        for _ in range(amount):
            if not deck:
                deck.extend(graveyard)
                graveyard.clear()
                random.shuffle(deck)
            if deck:
                hand.append(deck.pop(0))
        if is_player:
            self.p_deck, self.p_graveyard = deck, graveyard
        else:
            self.m_deck, self.m_graveyard = deck, graveyard
        return hand

    def get_layer1_counter(self, m_type):
        if m_type == 'ATK': return 'DEF'
        if m_type == 'DEF': return 'SPE'
        if m_type == 'SPE': return 'ATK'
        return None

    def auto_choose_card(self, hand, m_action):
        """AI BOT: Ưu tiên tuyệt đối Thắng Lớp 1 -> Hòa Lớp 1 -> Đành Thua"""
        counter_type = self.get_layer1_counter(m_action.type)
        
        # Ưu tiên 1: Tìm bài khắc chế Lớp 1
        counters = [c for c in hand if c.type == counter_type]
        if counters:
            return counters[0]
            
        # Ưu tiên 2: Tìm bài đọ Lớp 2 (Cùng hệ)
        ties = [c for c in hand if c.type == m_action.type]
        if ties:
            return ties[0]
            
        # Đường cùng: Đánh bài thua Lớp 1
        return hand[0]

    def resolve(self, p_card, m_card):
        # [Rút gọn Logic Va chạm để Code chạy nhanh]
        p_wins_l1 = (p_card.type == 'DEF' and m_card.type == 'ATK') or \
                    (p_card.type == 'ATK' and m_card.type == 'SPE') or \
                    (p_card.type == 'SPE' and m_card.type == 'DEF')
                    
        m_wins_l1 = (m_card.type == 'DEF' and p_card.type == 'ATK') or \
                    (m_card.type == 'ATK' and p_card.type == 'SPE') or \
                    (m_card.type == 'SPE' and p_card.type == 'DEF')

        if p_wins_l1:
            self.apply_effect(p_card, True, False)
        elif m_wins_l1:
            self.apply_effect(m_card, False, False)
        else:
            # Đọ Lớp 2
            if p_card.style == m_card.style: return
            p_wins_l2 = (p_card.style == 'Heavy' and m_card.style == 'Combo') or \
                        (p_card.style == 'Combo' and m_card.style == 'Light') or \
                        (p_card.style == 'Light' and m_card.style == 'Heavy')
            if p_wins_l2:
                self.apply_effect(p_card, True, True)
            else:
                self.apply_effect(m_card, False, True)

    def apply_effect(self, card, is_player, is_x2):
        val = card.value * (2 if is_x2 else 1)
        if card.type == 'ATK':
            if is_player: self.m_hp = max(0, self.m_hp - val)
            else: self.p_hp = max(0, self.p_hp - val)
        elif card.type == 'DEF':
            if card.style == 'Combo':
                if is_player: self.p_hp = min(100, self.p_hp + val)
                else: self.m_hp += val
            else:
                if is_player: self.p_mot += val
                else: self.p_mot -= val
        elif card.type == 'SPE':
            if card.style == 'Combo':
                if is_player: self.p_hp = min(100, self.p_hp + val)
                else: self.m_hp += val
            else:
                if is_player: self.p_cor -= val
                else: self.p_cor += val

    def run_game(self):
        while True:
            self.turns += 1
            hand = self.draw_cards(5, True)
            m_actions = self.draw_cards(3, False)
            
            p_choices = []
            for i in range(3):
                chosen = self.auto_choose_card(hand, m_actions[i])
                p_choices.append(chosen)
                hand.remove(chosen)
                
            for i in range(3):
                self.resolve(p_choices[i], m_actions[i])
                if self.p_hp <= 0: return "PLAYER_DEAD"
                if self.m_hp <= 0: return "MONSTER_DEAD"
                if self.p_mot <= 20 or self.p_mot >= 80 or self.p_cor <= 20 or self.p_cor >= 80:
                    return "STATUS_OOB"
                    
            self.p_graveyard.extend(p_choices + hand)
            self.m_graveyard.extend(m_actions)

# --- KHU VỰC THỐNG KÊ ---
SIMULATION_RUNS = 1000
results = {"MONSTER_DEAD": 0, "PLAYER_DEAD": 0, "STATUS_OOB": 0}
total_turns = 0

for _ in range(SIMULATION_RUNS):
    game = GameSim()
    outcome = game.run_game()
    results[outcome] += 1
    total_turns += game.turns

print(f"--- KẾT QUẢ MÔ PHỎNG {SIMULATION_RUNS} TRẬN ---")
print(f"Trung bình số Lượt (Turns) / Trận: {total_turns / SIMULATION_RUNS:.2f}")
print(f"Tỷ lệ Player THẮNG (Quái hết HP): {results['MONSTER_DEAD'] / SIMULATION_RUNS * 100:.1f}%")
print(f"Tỷ lệ Player THUA (Hết HP): {results['PLAYER_DEAD'] / SIMULATION_RUNS * 100:.1f}%")
print(f"Tỷ lệ Vỡ Trận Trạng Thái (MOT/COR): {results['STATUS_OOB'] / SIMULATION_RUNS * 100:.1f}%")