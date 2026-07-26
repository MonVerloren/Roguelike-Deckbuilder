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
                if is_player: 
                    self.p_hp = min(50, self.p_hp + val)
                else: 
                    # FIX: Khóa Max HP 50 cho quái
                    self.m_hp = min(50, self.m_hp + val) 
                print(Fore.GREEN +  f"  -> {'Bạn' if is_player else 'Quái'} hồi {val} HP")
            else:
                if is_player: self.p_mot += val
                else: self.p_mot -= val
                print(Fore.YELLOW + f"  -> Motivation {'tăng' if is_player else 'giảm'} {val}. Hiện tại: {self.p_mot}")
                
        elif card.type == 'SPE':
            if card.style == 'Combo':
                if is_player: 
                    self.p_hp = min(50, self.p_hp + val)
                else: 
                    # FIX: Khóa Max HP 50 cho quái
                    self.m_hp = min(50, self.m_hp + val)
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

        # 1. RÚT BÀI
        hand = self.draw_cards(5, is_player=True)
        m_hand = self.draw_cards(5, is_player=False)
        
        # Quái rút 5 lá nhưng chỉ chọn 3 lá ngẫu nhiên để đánh
        m_actions = random.sample(m_hand, 3)
        unused_m_cards = [c for c in m_hand if c not in m_actions]

        # 2. HỆ THỐNG TÍN HIỆU HÀNH VI (TELEGRAPHING)
        atk_c = sum(1 for c in m_actions if c.type == 'ATK')
        def_c = sum(1 for c in m_actions if c.type == 'DEF')
        spe_c = sum(1 for c in m_actions if c.type == 'SPE')
        
        telegraph_msg = ""
        if atk_c == 3:
            telegraph_msg = "[!] Quái vật vào trạng thái CUỒNG NỘ!"
        elif atk_c == 2:
            telegraph_msg = "[!] Quái vật đang NỔI ĐIÊN!"
        elif atk_c == 0: 
            # 3 lá chỉ toàn DEF và SPE (0 ATK) - Random 1 trong 2
            telegraph_msg = random.choice([
                "[!] Quái vật đang HOẢNG SỢ!", 
                "[!] Quái vật đang HOẢNG LOẠN!"
            ])
        elif atk_c == 1 and (def_c == 0 or spe_c == 0):
            # 1 ATK, 2 DEF, 0 SPE HOẶC 1 ATK, 0 DEF, 2 SPE - Random 1 trong 2
            telegraph_msg = random.choice([
                "[!] Quái vật đang E DÈ.", 
                "[!] Quái vật đang THĂM DÒ."
            ])
        # Trường hợp 1 ATK, 1 DEF, 1 SPE: telegraph_msg giữ nguyên là "" (Không hiện gì)

        # 3. HIỂN THỊ UI
        print(Fore.GREEN + f"\n[THÔNG TIN BÀI BẠN] Deck: {len(self.p_deck)} lá | Mộ: {len(self.p_graveyard)} lá")
        
        # In Tín hiệu Hành vi nếu có
        if telegraph_msg:
            print(Fore.CYAN + telegraph_msg)
            
        # Chỉ tiết lộ Lớp 2 (Style) của Quái vật
        print(Fore.RED + f"Quái vật chuẩn bị đánh (Lớp 2): {[card.style for card in m_actions]}")

        # 4. CHỌN BÀI TỪ NGƯỜI CHƠI
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
                    
        # 5. THỰC THI VA CHẠM
        os.system("cls" if os.name == "nt" else "clear")
        print(Fore.YELLOW + "--- KẾT QUẢ VA CHẠM ---")
        for i in range(3):
            self.clash(p_choices[i], m_actions[i])
            if self.p_hp <= 0 or self.m_hp <= 0:
                print("\n[!] Trận đấu kết thúc!")
                break

        # 6. DỌN MỘ BÀI ĐÚNG QUY TẮC CHO CẢ 2 BÊN
        self.p_graveyard.extend(p_choices)
        self.p_graveyard.extend(hand) # Bài dư trên tay Player
        
        self.m_graveyard.extend(m_actions)
        self.m_graveyard.extend(unused_m_cards) # 2 lá Quái không xài

        return self.check_status()

# Khởi chạy Game Loop
if __name__ == "__main__":
    game = Game()
    while game.play_turn():
        pass