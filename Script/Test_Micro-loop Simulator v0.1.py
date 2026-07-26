import random
import os
from colorama import Fore, init

# ==========================================
# CẤU HÌNH CƠ BẢN
# ==========================================
init(autoreset=True)
TYPES = ['ATK', 'DEF', 'SPE']
STYLES = {'Light': 7, 'Combo': 9, 'Heavy': 11}

class Card:
    def __init__(self, card_type, style):
        self.type = card_type
        self.style = style
        self.value = STYLES[style]

    def __repr__(self):
        return f"[{self.type}-{self.style}]"

class Game:
    def __init__(self):
        #Turn
        self.turn_count =0

        # Chỉ số người chơi
        self.p_hp = 50
        self.p_mot = 50
        self.p_cor = 50
        
        # Quái vật mô phỏng
        self.m_hp = 50

        # 1. THIẾT LẬP BỘ BÀI NGƯỜI CHƠI (Cân bằng)
        self.p_deck = [
            Card('ATK', 'Light'), Card('ATK', 'Combo'), Card('ATK', 'Heavy'), Card('ATK', 'Light'), Card('ATK', 'Combo'),
            Card('DEF', 'Light'), Card('DEF', 'Combo'), Card('DEF', 'Heavy'), Card('DEF', 'Combo'), Card('DEF', 'Light'),
            Card('SPE', 'Light'), Card('SPE', 'Combo'), Card('SPE', 'Heavy'), Card('SPE', 'Light'), Card('SPE', 'Combo')
        ]
        self.p_graveyard = []
        random.shuffle(self.p_deck)

        # 2. THIẾT LẬP BỘ BÀI QUÁI VẬT (Thiên hướng Cuồng Nộ: Nhiều ATK)
        self.m_deck = [
            Card('ATK', 'Heavy'), Card('ATK', 'Heavy'), Card('ATK', 'Combo'), Card('ATK', 'Combo'), Card('ATK', 'Combo'),
            Card('ATK', 'Light'), Card('ATK', 'Light'), Card('DEF', 'Heavy'), Card('DEF', 'Combo'), Card('DEF', 'Light'),
            Card('SPE', 'Heavy'), Card('SPE', 'Combo'), Card('SPE', 'Light'), Card('ATK', 'Light'), Card('ATK', 'Light')
        ]
        self.m_graveyard = []
        random.shuffle(self.m_deck)
        
    # # Khởi tạo bộ bài 15 lá CỐ ĐỊNH từ đầu trận
    # self.card_pool = [Card(t, s) for t in TYPES for s in STYLES.keys()]
    # self.deck = [random.choice(self.card_pool) for _ in range(15)]
    # self.graveyard = []
        
    # def generate_deck(self, size=15):
    #     return [random.choice(self.card_pool) for _ in range(size)]

    # def draw_cards(self, amount=5):
    #     """Cơ chế rút bài từ Deck, xáo lại từ Mộ nếu hết bài"""
    #     hand = []
    #     for _ in range(amount):
    #         if len(self.deck) == 0:
    #             print("\n[HỆ THỐNG] Bộ bài đã cạn! Đang xáo lại bài từ Mộ lên Bộ bài...")
    #             self.deck = self.graveyard.copy()
    #             self.graveyard = []
    #             random.shuffle(self.deck) # Xáo trộn bài
            
    #         if len(self.deck) > 0:
    #             hand.append(self.deck.pop(0))
    #     return hand

    def draw_cards(self, amount, is_player=True):
        """Hàm rút bài chung cho cả Người và Quái"""
        hand = []
        deck = self.p_deck if is_player else self.m_deck
        graveyard = self.p_graveyard if is_player else self.m_graveyard
        
        for _ in range(amount):
            if len(deck) == 0:
                if is_player: print("\n[HỆ THỐNG] Bộ bài của BẠN đã cạn! Xáo lại bài từ Mộ...")
                deck.extend(graveyard)
                graveyard.clear()
                random.shuffle(deck)
            
            if len(deck) > 0:
                hand.append(deck.pop(0))
                
        # Cập nhật lại mảng gốc sau khi thao tác
        if is_player:
            self.p_deck = deck
            self.p_graveyard = graveyard
        else:
            self.m_deck = deck
            self.m_graveyard = graveyard
            
        return hand

    def resolve_effect(self, card, is_player, is_x2=False):
        """Xử lý tác động của thẻ bài lên chỉ số"""
        multiplier = 2 if is_x2 else 1
        val = card.value * multiplier
        
        if card.type == 'ATK':
            if is_player:
                self.m_hp = max(0, self.m_hp - val)
                print(Fore.RED + f"  -> Bạn gây {val} sát thương. Quái còn {self.m_hp} HP")
            else:
                self.p_hp = max(0, self.p_hp - val)
                print(Fore.RED + f"  -> Quái gây {val} sát thương. Bạn còn {self.p_hp} HP")
                
        elif card.type == 'DEF':
            if card.style == 'Combo':
                if is_player: self.p_hp = min(50, self.p_hp + val)
                else: self.m_hp += val
                print(Fore.GREEN +  f"  -> {'Bạn' if is_player else 'Quái'} hồi {val} HP")
            else:
                if is_player: self.p_mot += val
                else: self.p_mot -= val
                print(Fore.YELLOW + f"  -> Motivation {'tăng' if is_player else 'giảm'} {val}. Hiện tại: {self.p_mot}")
                
        elif card.type == 'SPE':
            if card.style == 'Combo':
                if is_player: self.p_hp = min(50, self.p_hp + val)
                else: self.m_hp += val
                print(Fore.GREEN + f"  -> {'Bạn' if is_player else 'Quái'} hồi {val} HP")
            else:
                if is_player: self.p_cor -= val
                else: self.p_cor += val
                print(Fore.YELLOW + f"  -> Corruption {'giảm' if is_player else 'tăng'} {val}. Hiện tại: {self.p_cor}")

    def clash(self, p_card, m_card):
        """Ma trận xử lý va chạm Kéo-Búa-Bao kép"""
        print(f"\nVa chạm: {p_card} vs {m_card}")
        
        # 1. TRƯỜNG HỢP CÙNG HỆ CHÍNH (Đọ Lớp 2)
        if p_card.type == m_card.type:
            if p_card.style == m_card.style:
                print("  -> Hòa Lớp 2! Hai đòn triệt tiêu nhau.")
                return
            
            # Logic hệ phụ: Heavy(7) > Combo(5) > Light(3) > Heavy(7)
            p_wins_sub = (p_card.style == 'Heavy' and m_card.style == 'Combo') or \
                         (p_card.style == 'Combo' and m_card.style == 'Light') or \
                         (p_card.style == 'Light' and m_card.style == 'Heavy')
                         
            if p_wins_sub:
                print(Fore.GREEN + f"  -> Bạn THẮNG Lớp 2! Kích hoạt x2 {p_card.type}.")
                self.resolve_effect(p_card, is_player=True, is_x2=True)
            else:
                print(Fore.RED + f"  -> Quái THẮNG Lớp 2! Kích hoạt x2 {m_card.type}.")
                self.resolve_effect(m_card, is_player=False, is_x2=True)
                
        # 2. TRƯỜNG HỢP KHÁC HỆ CHÍNH (Khắc chế Lớp 1)
        else:
            # Rule: DEF > ATK, ATK > SPE, SPE > DEF
            p_wins_l1 = (p_card.type == 'DEF' and m_card.type == 'ATK') or \
                        (p_card.type == 'ATK' and m_card.type == 'SPE') or \
                        (p_card.type == 'SPE' and m_card.type == 'DEF')
            
            if p_wins_l1:
                print("  -> Bạn THẮNG Lớp 1 (Áp đảo)! Đòn của quái bị triệt tiêu.")
                self.resolve_effect(p_card, is_player=True, is_x2=False)
            else:
                print("  -> Quái THẮNG Lớp 1 (Áp đảo)! Đòn của bạn bị triệt tiêu.")
                self.resolve_effect(m_card, is_player=False, is_x2=False)

    def check_status(self, is_start_of_turn=False):
        """Kiểm tra và hiển thị trạng thái"""
        # Cập nhật hiển thị: Thêm Máu quái và hiển thị rõ ràng hơn
        print(Fore.GREEN + f"\n[STATUS]\n HP BẠN: {self.p_hp}/50 | MOT: {self.p_mot} | COR: {self.p_cor}\n HP QUÁI: {self.m_hp}/50")
        print(Fore.YELLOW + f"\n ATK>SPE>DEF>ATK\n LIGHT>HEAVY>COMBO>LIGHT") 
        
        if self.p_hp <= 0:
            print(Fore.RED + ">>> GAME OVER: Bạn đã hết máu!")
            return False
        if self.m_hp <= 0:
            print(Fore.GREEN + ">>> CHIẾN THẮNG: Quái vật đã bị tiêu diệt!")
            return False
        if self.p_mot >= 80 or self.p_mot <= 20 or self.p_cor >= 80 or self.p_cor <= 20:
            print(Fore.RED + ">>> GAME OVER: Chỉ số Trạng thái đã vượt ngưỡng an toàn (20-80)!")
            return False
        return True

    def play_turn(self):
        # Đánh số turn
        self.turn_count += 1  

        # Setup lượt đấu
        print("\n" + "="*50)
        print(Fore.YELLOW + f"LƯỢT [ {self.turn_count} ] BẮT ĐẦU")

        if not self.check_status(is_start_of_turn=True):
            return False

        # Người chơi rút 5 lá, Quái rút 3 lá TỪ BỘ BÀI CỦA CHÚNG
        hand = self.draw_cards(5, is_player=True)
        m_actions = self.draw_cards(3, is_player=False) # QUÁI CŨNG RÚT BÀI CÓ TÍNH TOÁN

    # # 1. Rút 5 lá bài theo đúng cơ chế
    # hand = self.draw_cards(5)
        
    # # Quái vật rút 3 lá ngẫu nhiên (Giả định quái không dùng chung Deck)
    # m_actions = [random.choice(self.card_pool) for _ in range(3)]
        
        # 2. Hiển thị UI Deck & Graveyard
    # print(f"\n[THÔNG TIN BÀI] Bộ bài (Deck) còn: {len(self.deck)} lá | Mộ (Graveyard) có: {len(self.graveyard)} lá")
    # print(f"Quái vật chuẩn bị đánh: {[card.type for card in m_actions]}")
        print(Fore.GREEN + f"\n[THÔNG TIN BÀI BẠN] Deck: {len(self.p_deck)} lá | Mộ: {len(self.p_graveyard)} lá")
        print(Fore.RED + f"Quái vật chuẩn bị đánh: {[card.type for card in m_actions]}")

    # deck = self.generate_deck(15)
    # hand = deck[:5]
    # m_actions = [random.choice(self.card_pool) for _ in range(3)]      
    # print("Quái vật chuẩn bị đánh:", [card.type for card in m_actions])
        
        p_choices = []
        for i in range(3):
            print(Fore.GREEN + f"\nTrên tay bạn có: {[(idx, str(c)) for idx, c in enumerate(hand)]}")
            while True:
                try:
                    choice = int(input(f"Chọn lá bài thứ {i+1} để đối phó (nhập ID từ 0 tới {len(hand)-1}): "))
                    if 0 <= choice < len(hand):
                        p_choices.append(hand.pop(choice))
                        break
                    else:
                        print("ID không hợp lệ.")
                except ValueError:
                    print("Vui lòng nhập số nguyên.")
                    
        # Thực thi chuỗi va chạm
        os.system("cls" if os.name == "nt" else "clear")
        print(Fore.YELLOW + "--- KẾT QUẢ VA CHẠM ---")
        for i in range(3):
            self.clash(p_choices[i], m_actions[i])
            if self.p_hp <= 0 or self.m_hp <= 0:
                print("\n[!] Trận đấu kết thúc!")
                break

    # # 4. Bỏ bài thừa và bài đã đánh xuống Mộ
    # self.graveyard.extend(p_choices)
    # self.graveyard.extend(hand)  

        self.p_graveyard.extend(p_choices)
        self.p_graveyard.extend(hand)
        self.m_graveyard.extend(m_actions)

        return self.check_status()

# Khởi chạy Game Loop
if __name__ == "__main__":
    game = Game()
    while game.play_turn():
        pass