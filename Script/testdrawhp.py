import random

TYPES = ['ATK', 'DEF', 'SPE']
STYLES = {'Light': 7, 'Combo': 9, 'Heavy': 11}

class Card:
    def __init__(self, card_type, style):
        self.type = card_type
        self.style = style
        self.value = STYLES[style]
    def __repr__(self):
        return f"[{self.type}-{self.style}]"

class GameSimV2:
    def __init__(self):
        self.turn_count = 0
        self.p_hp = 50
        self.p_mot = 50
        self.p_cor = 50
        self.m_hp = 50
        self.clash_pot = 0 # Biến lưu trữ điểm Tích tụ từ các pha Hòa

        self.p_deck = [Card(t, s) for t in TYPES for s in STYLES.keys()] + [Card('ATK', 'Combo'), Card('DEF', 'Heavy'), Card('SPE', 'Light'), Card('ATK', 'Light'), Card('DEF', 'Combo')]
        self.p_graveyard = []
        random.shuffle(self.p_deck)

        self.m_deck = [Card('ATK', 'Heavy')]*2 + [Card('ATK', 'Combo')]*3 + [Card('ATK', 'Light')]*2 + [Card('DEF', 'Heavy'), Card('DEF', 'Combo'), Card('DEF', 'Light'), Card('SPE', 'Heavy'), Card('SPE', 'Combo'), Card('SPE', 'Light'), Card('ATK', 'Light'), Card('ATK', 'Light')]
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
            if deck: hand.append(deck.pop(0))
        return hand

    def apply_effect(self, card, is_player, is_x2=False):
        # VERSION 2: Val hoạt động độc lập, Pot chỉ trừ máu
        val = card.value * (2 if is_x2 else 1)
        bonus_hp_damage = self.clash_pot
        self.clash_pot = 0 # Reset pot sau khi có người ăn
        
        # 1. Thực thi hiệu ứng gốc của thẻ bài
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

        # 2. Xả toàn bộ Pot thành sát thương trừ thẳng vào HP kẻ thua
        if bonus_hp_damage > 0:
            if is_player: self.m_hp = max(0, self.m_hp - bonus_hp_damage)
            else: self.p_hp = max(0, self.p_hp - bonus_hp_damage)

    def clash(self, p_card, m_card):
        if p_card.type == m_card.type:
            if p_card.style == m_card.style: 
                self.clash_pot += p_card.value # Hòa tuyệt đối -> Nhồi giá trị vào Pot
                return
            p_wins_sub = (p_card.style == 'Heavy' and m_card.style == 'Combo') or \
                         (p_card.style == 'Combo' and m_card.style == 'Light') or \
                         (p_card.style == 'Light' and m_card.style == 'Heavy')
            if p_wins_sub: self.apply_effect(p_card, True, True)
            else: self.apply_effect(m_card, False, True)
        else:
            p_wins_l1 = (p_card.type == 'DEF' and m_card.type == 'ATK') or \
                        (p_card.type == 'ATK' and m_card.type == 'SPE') or \
                        (p_card.type == 'SPE' and m_card.type == 'DEF')
            if p_wins_l1: self.apply_effect(p_card, True, False)
            else: self.apply_effect(m_card, False, False)

    def auto_choose(self, hand, m_action, state_signal):
        if state_signal == "CUONG_NO":
            def_cards = [c for c in hand if c.type == 'DEF']
            if def_cards: return def_cards[0]
        if state_signal == "HOANG_SO":
            atk_cards = [c for c in hand if c.type == 'ATK']
            if atk_cards: return atk_cards[0]
        counter_style = {'Heavy': 'Light', 'Combo': 'Heavy', 'Light': 'Combo'}[m_action.style]
        l2_counters = [c for c in hand if c.style == counter_style]
        if l2_counters: return l2_counters[0]
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

            atk_c = sum(1 for c in m_actions if c.type == 'ATK')
            state_signal = "NORMAL"
            if atk_c == 3: state_signal = "CUONG_NO"
            elif atk_c == 2: state_signal = "NOI_DIEN"
            elif atk_c == 0: state_signal = "HOANG_SO"
            elif atk_c == 1: state_signal = "E_DE" 

            p_choices = []
            for i in range(3):
                chosen = self.auto_choose(hand, m_actions[i], state_signal)
                p_choices.append(chosen)
                hand.remove(chosen)
                
            for i in range(3):
                self.clash(p_choices[i], m_actions[i])
                if self.p_hp <= 0: return "PLAYER_DEAD", self.p_hp
                if self.m_hp <= 0: return "MONSTER_DEAD", self.p_hp
                if self.p_mot >= 80 or self.p_mot <= 20 or self.p_cor >= 80 or self.p_cor <= 20: return "STATUS_OOB", self.p_hp

            self.p_graveyard.extend(p_choices + hand)
            self.m_graveyard.extend(m_actions + unused_m_cards)

def run_sim_v2(runs=10000):
    results = {"MONSTER_DEAD": 0, "PLAYER_DEAD": 0, "STATUS_OOB": 0}
    total_turns, total_hp_when_won = 0, 0
    for _ in range(runs):
        game = GameSimV2()
        outcome, final_hp = game.run_game()
        results[outcome] += 1
        total_turns += game.turn_count
        if outcome == "MONSTER_DEAD": total_hp_when_won += final_hp
    
    print(f"\n--- PHIÊN BẢN 2: TÍCH TỤ CHỈ TRỪ VÀO HP ({runs} trận) ---")
    print(f"Lượt trung bình: {total_turns / runs:.2f}")
    print(f"Tỷ lệ THẮNG: {results['MONSTER_DEAD'] / runs * 100:.1f}% (HP còn: {total_hp_when_won/max(1, results['MONSTER_DEAD']):.1f}/50)")
    print(f"Tỷ lệ THUA (Hết HP): {results['PLAYER_DEAD'] / runs * 100:.1f}%")
    print(f"Tỷ lệ THUA (Vỡ MOT/COR): {results['STATUS_OOB'] / runs * 100:.1f}%")

run_sim_v2()