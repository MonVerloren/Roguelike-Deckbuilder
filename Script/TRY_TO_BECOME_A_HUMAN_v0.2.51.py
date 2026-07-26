import random
import os
import json
import msvcrt
from colorama import Fore, init

# ==========================================
# CẤU HÌNH CƠ BẢN
# ==========================================
init(autoreset=True)
TYPES = ['ATK', 'DEF', 'SPE']
STYLES = {'Light': 7, 'Combo': 9, 'Heavy': 11}
LEADERBOARD_FILE = "leaderboard.json"

class Card:
    def __init__(self, card_type, style):
        self.type = card_type
        self.style = style
        self.value = STYLES[style]

    def __repr__(self):
        return f"[{self.type}-{self.style}]"

class Game:
    def get_player_keypress(self, max_id):
        """Hàm đọc phím trực tiếp không cần nhấn Enter"""
        while True:
            if msvcrt.kbhit():
                key = msvcrt.getch()
                
                # Bắt mã phím ESC (Mã ASCII hoặc Hex là \x1b)
                if key == b'\x1b': 
                    return "ESC"
                
                # Bắt các phím số
                try:
                    char = key.decode('utf-8')
                    choice = int(char)
                    if 0 <= choice <= max_id:
                        return choice
                except ValueError:
                    pass # Bỏ qua nếu người chơi bấm linh tinh
    def __init__(self, game_number=1, p_hp=50, p_mot=50, p_cor=50):
        self.game_number = game_number
        self.turn_count = 0

        # Chỉ số người chơi (Được kế thừa nếu chơi tiếp)
        self.p_hp = p_hp
        self.p_mot = p_mot
        self.p_cor = p_cor
        
        # Quái vật mới luôn đầy 50 HP
        self.m_hp = 50

        # 1. THIẾT LẬP BỘ BÀI NGƯỜI CHƠI
        self.p_deck = [
            Card('ATK', 'Light'), Card('ATK', 'Combo'), Card('ATK', 'Heavy'), Card('ATK', 'Light'), Card('ATK', 'Combo'),
            Card('DEF', 'Light'), Card('DEF', 'Combo'), Card('DEF', 'Heavy'), Card('DEF', 'Combo'), Card('DEF', 'Light'),
            Card('SPE', 'Light'), Card('SPE', 'Combo'), Card('SPE', 'Heavy'), Card('SPE', 'Light'), Card('SPE', 'Combo')
        ]
        self.p_graveyard = []
        random.shuffle(self.p_deck)

        # 2. THIẾT LẬP BỘ BÀI QUÁI VẬT
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
                if is_player: print(Fore.CYAN + "\n[HỆ THỐNG] Bộ bài của BẠN đã cạn! Xáo lại bài từ Mộ...")
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

    def resolve_effect(self, card, is_player, is_x2=False):
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
                    self.m_hp = min(50, self.m_hp + val)
                print(Fore.GREEN + f"  -> {'Bạn' if is_player else 'Quái'} hồi {val} HP")
            else:
                if is_player: self.p_cor -= val
                else: self.p_cor += val
                print(Fore.YELLOW + f"  -> Corruption {'giảm' if is_player else 'tăng'} {val}. Hiện tại: {self.p_cor}")

    def clash(self, p_card, m_card):
        print(f"\nVa chạm: {p_card} vs {m_card}")
        if p_card.type == m_card.type:
            if p_card.style == m_card.style:
                print("  -> Hòa Style! Hai đòn triệt tiêu nhau.")
                return
            p_wins_sub = (p_card.style == 'Heavy' and m_card.style == 'Combo') or \
                         (p_card.style == 'Combo' and m_card.style == 'Light') or \
                         (p_card.style == 'Light' and m_card.style == 'Heavy')
            if p_wins_sub:
                print(Fore.GREEN + f"  -> Bạn THẮNG Style! Kích hoạt x2 {p_card.type}.")
                self.resolve_effect(p_card, is_player=True, is_x2=True)
            else:
                print(Fore.RED + f"  -> Quái THẮNG Style! Kích hoạt x2 {m_card.type}.")
                self.resolve_effect(m_card, is_player=False, is_x2=True)
        else:
            p_wins_l1 = (p_card.type == 'DEF' and m_card.type == 'ATK') or \
                        (p_card.type == 'ATK' and m_card.type == 'SPE') or \
                        (p_card.type == 'SPE' and m_card.type == 'DEF')
            if p_wins_l1:
                print("  -> Bạn THẮNG Type (Áp đảo)! Đòn của quái bị triệt tiêu.")
                self.resolve_effect(p_card, is_player=True, is_x2=False)
            else:
                print("  -> Quái THẮNG Type (Áp đảo)! Đòn của bạn bị triệt tiêu.")
                self.resolve_effect(m_card, is_player=False, is_x2=False)

    def check_status(self, is_start_of_turn=False):
        if not is_start_of_turn:
            print("\n" + "-"*30)
            
        print(Fore.GREEN + f"[STATUS]\n HP BẠN: {self.p_hp}/50 | MOT: {self.p_mot} | COR: {self.p_cor}\n HP QUÁI: {self.m_hp}/50")
        print(Fore.YELLOW + f"\n ATK>SPE>DEF>ATK\n LIGHT>HEAVY>COMBO>LIGHT") 
        
        if self.p_hp <= 0:
            print(Fore.RED + "\n>>> GAME OVER: Bạn đã hết máu!")
            return "LOSE"
        if self.m_hp <= 0:
            print(Fore.GREEN + "\n>>> CHIẾN THẮNG: Quái vật đã bị tiêu diệt!")
            return "WIN"
        if self.p_mot >= 80 or self.p_mot <= 20 or self.p_cor >= 80 or self.p_cor <= 20:
            print(Fore.RED + "\n>>> GAME OVER: Chỉ số Trạng thái đã vượt ngưỡng an toàn (20-80)!")
            return "LOSE"
            
        return "CONTINUE"

    def play_turn(self):
        self.turn_count += 1  
        
        print("\n" + "="*50)
        # Bổ sung Text Game [n] ở trên Turn
        print(Fore.YELLOW + f"Nhấn ESC để thoát\n")
        print(Fore.CYAN + f"GAME [ {self.game_number} ]")
        print(Fore.YELLOW + f"LƯỢT [ {self.turn_count} ] BẮT ĐẦU\n")

        status = self.check_status(is_start_of_turn=True)
        if status != "CONTINUE":
            return status

        hand = self.draw_cards(5, is_player=True)
        m_hand = self.draw_cards(5, is_player=False)
        m_actions = random.sample(m_hand, 3)
        unused_m_cards = [c for c in m_hand if c not in m_actions]

        atk_c = sum(1 for c in m_actions if c.type == 'ATK')
        def_c = sum(1 for c in m_actions if c.type == 'DEF')
        spe_c = sum(1 for c in m_actions if c.type == 'SPE')
        
        telegraph_msg = ""
        if atk_c == 3: telegraph_msg = "[!] Quái vật vào trạng thái CUỒNG NỘ!"
        elif atk_c == 2: telegraph_msg = "[!] Quái vật đang NỔI ĐIÊN!"
        elif atk_c == 0: 
            telegraph_msg = random.choice(["[!] Quái vật đang HOẢNG SỢ!", "[!] Quái vật đang HOẢNG LOẠN!"])
        elif atk_c == 1 and (def_c == 0 or spe_c == 0):
            telegraph_msg = random.choice(["[!] Quái vật đang E DÈ.", "[!] Quái vật đang THĂM DÒ."])

        print(Fore.GREEN + f"\n[THÔNG TIN BÀI BẠN] Deck: {len(self.p_deck)} lá | Mộ: {len(self.p_graveyard)} lá")
        if telegraph_msg: print(Fore.CYAN + telegraph_msg)
        print(Fore.RED + f"Quái vật chuẩn bị đánh (Style): {[card.style for card in m_actions]}")

        p_choices = []
        for i in range(3):
            print(Fore.GREEN + f"\nTrên tay bạn có: {[(idx, str(c)) for idx, c in enumerate(hand)]}")
            print(Fore.CYAN + f"Chọn lá thứ {i+1} (Nhấn 0 tới {len(hand)-1}): ", end="", flush=True)
            
            # Gọi hàm bắt phím trực tiếp
            choice = self.get_player_keypress(len(hand)-1)
            
            # Xử lý khi nhấn ESC
            if choice == "ESC":
                print(Fore.YELLOW + "\n\n[!] Đang thoát về Main Menu...")
                return "ESCAPE" # Trả về trạng thái mới
                
            print(choice) # In số người chơi vừa bấm ra màn hình cho tự nhiên
            p_choices.append(hand.pop(choice))
                    
        os.system("cls" if os.name == "nt" else "clear")
        print(Fore.YELLOW + "--- KẾT QUẢ VA CHẠM ---")
        for i in range(3):
            self.clash(p_choices[i], m_actions[i])
            if self.p_hp <= 0 or self.m_hp <= 0:
                print("\n[!] Trận đấu kết thúc sớm!")
                break

        self.p_graveyard.extend(p_choices + hand)
        self.m_graveyard.extend(m_actions + unused_m_cards)

        return self.check_status()

# ==========================================
# HỆ THỐNG MENU & BẢNG XẾP HẠNG
# ==========================================
SAVE_FILE = "savegame.json"

def load_leaderboard():
    if os.path.exists(LEADERBOARD_FILE):
        try:
            with open(LEADERBOARD_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def save_score(name, games_survived):
    if games_survived <= 0: return 
    
    board = load_leaderboard()
    board.append({"name": name, "score": games_survived})
    board = sorted(board, key=lambda x: x["score"], reverse=True)[:10]
    
    with open(LEADERBOARD_FILE, 'w', encoding='utf-8') as f:
        json.dump(board, f, ensure_ascii=False, indent=4)

def save_game_state(name, game_number, hp, mot, cor):
    """Lưu tiến trình của người chơi vào file"""
    saves = {}
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, 'r', encoding='utf-8') as f:
                saves = json.load(f)
        except:
            pass
            
    saves[name] = {
        "game_number": game_number,
        "hp": hp,
        "mot": mot,
        "cor": cor
    }
    
    with open(SAVE_FILE, 'w', encoding='utf-8') as f:
        json.dump(saves, f, ensure_ascii=False, indent=4)

def load_game_state(name):
    """Đọc tiến trình cũ"""
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, 'r', encoding='utf-8') as f:
                saves = json.load(f)
                return saves.get(name)
        except:
            return None
    return None

def clear_save(name):
    """Xóa file save khi Game Over hoặc Thoát"""
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, 'r', encoding='utf-8') as f:
                saves = json.load(f)
            if name in saves:
                del saves[name]
                with open(SAVE_FILE, 'w', encoding='utf-8') as f:
                    json.dump(saves, f, ensure_ascii=False, indent=4)
        except:
            pass

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def show_tutorial():
    clear_screen()
    print(Fore.CYAN + "=== HƯỚNG DẪN CHƠI ===")
    print("1. Trò chơi sử dụng hệ thống Kéo-Búa-Bao KÉP.")
    print("2. Type: DEF > ATK > SPE > DEF.")
    print("3. Stlye: Heavy > Combo > Light > Heavy (Chỉ xét khi Type hòa và nếu thắng bằng Style mọi chỉ số tác động đều được x2).")
    print("4. ATK: gây Sát Thương (HP) với các mốc 7/9/11 tương ứng với Light/Combo/Heavy.")
    print("5. Def: thành công sẽ tăng Chiến Ý (MOT) với các mốc 7/11 tương ứng với Light/Heavy. Thất Bại sẽ giảm chỉ số tương ứng.")
    print("6. Spe: thành công sẽ giảm Tỉnh Táo (COR) với các mốc 7/11 tương ứng với Light/Heavy. Thất Bại sẽ tăng chỉ số tương ứng.")
    print("7. Nếu HP=0 hoặc 20<COR<80 hoặc 20<COR<80 đều sẽ Game Over.")
    print("8. Đừng lo nếu Def hay Spe Combo bạn sẽ được hồi 9 HP ... à mà quái cũng thế :>")
    print("9. Khi quái vật tấn công sẽ tiết lộ Style và cảnh báo trạng thái, hãy dựa vào cảnh báo đó để dự đoán Type.")
    print("10. Trạng thái: Cuồng nộ/Nổi điên - đa số ATK, Hoảng sợ/Hoảng loạn - đa số Def/Spe và các trạng thái còn lại.")
    print(Fore.CYAN + "Sống sót càng lâu càng tốt. Good Luck!")
    input(Fore.YELLOW + "\nNhấn Enter để quay lại Main Menu...")

def show_leaderboard():
    clear_screen()
    print(Fore.CYAN + "=== BẢNG XẾP HẠNG (TOP 10) ===")
    board = load_leaderboard()
    if not board:
        print("Chưa có kỷ lục nào được ghi nhận.")
    else:
        for idx, entry in enumerate(board):
            print(f"{idx + 1}. {entry['name']} - Sống sót: {entry['score']} Game")
    input(Fore.YELLOW + "\nNhấn Enter để quay lại Main Menu...")

def main_menu():
    while True:
        clear_screen()
        print(Fore.GREEN + "="*30)
        print(Fore.GREEN + "      CARD BATTLE\nTRY TO BECOME A HUMAN")
        print(Fore.GREEN + "="*30)
        print("1. Chơi")
        print("2. Hướng dẫn")
        print("3. Bảng xếp hạng")
        print("4. Thoát")
        print("="*30)
        
        choice = input("Vui lòng chọn (1-4): ")
        
        if choice == '1':
            player_name = input("Nhập tên của bạn (để lưu Bảng xếp hạng): ").strip()
            if not player_name: player_name = "PlayerKhuyetDanh"
            play_session(player_name)
        elif choice == '2':
            show_tutorial()
        elif choice == '3':
            show_leaderboard()
        elif choice == '4':
            print("Cảm ơn bạn đã chơi!")
            break
        else:
            print("Lựa chọn không hợp lệ!")

def play_session(player_name):
    # Kiểm tra xem người chơi này có file save cũ không
    saved_data = load_game_state(player_name)
    if saved_data:
        print(Fore.CYAN + f"\n[!] Tìm thấy tiến trình đang chơi dở của {player_name} (Tới Game {saved_data['game_number']}).")
        choice = input("\n(1) Tiếp tục chơi\n(2) Xóa save và Chơi mới từ đầu?\n Vui lòng chọn(1-2): ")
        if choice == '1':
            game_number = saved_data['game_number']
            current_hp = saved_data['hp']
            current_mot = saved_data['mot']
            current_cor = saved_data['cor']
        else:
            game_number = 1
            current_hp, current_mot, current_cor = 50, 50, 50
            clear_save(player_name)
    else:
        game_number = 1
        current_hp, current_mot, current_cor = 50, 50, 50
    
    while True:
        clear_screen()
        game = Game(game_number, current_hp, current_mot, current_cor)
        status = "CONTINUE"
        
        while status == "CONTINUE":
            status = game.play_turn()

        # --- XỬ LÝ NÚT ESC ---
        if status == "ESCAPE":
            return # Thoát thẳng hàm play_session, đưa người chơi về lại Main Menu
            
        # XỬ LÝ KẾT QUẢ KHI KẾT THÚC 1 GAME
        if status == "WIN":
            print(Fore.GREEN + f"\nChúc mừng! Bạn đã vượt qua Game {game_number}.")
            while True:
                print(Fore.CYAN + "\nBạn muốn:")
                print(" (1) Chơi tiếp [Kế thừa chỉ số]")
                print(" (2) Lưu Game & Thoát về Menu")
                print(" (3) Lưu Điểm Xếp Hạng & Thoát (End Game)")
                nxt = input("Vui lòng chọn(1-3): ")
                
                if nxt == '1':
                    game_number += 1
                    current_hp = game.p_hp
                    current_mot = game.p_mot
                    current_cor = game.p_cor
                    break
                elif nxt == '2':
                    game_number += 1
                    save_game_state(player_name, game_number, game.p_hp, game.p_mot, game.p_cor)
                    print(Fore.GREEN + f"Đã lưu tiến trình thành công cho {player_name}!")
                    input(Fore.YELLOW + "Nhấn Enter để quay lại Main Menu...")
                    return
                elif nxt == '3':
                    save_score(player_name, game_number)
                    clear_save(player_name) # Xóa file save vì đã chốt điểm
                    return
                else:
                    print("Lựa chọn không hợp lệ.")
                    
        elif status == "LOSE":
            print(Fore.YELLOW + f"Đã sống sót qua {game_number - 1} Game")
            save_score(player_name, game_number - 1)
            clear_save(player_name) # Game Over thì file save bay màu
            
            while True:
                nxt = input(Fore.CYAN + "\n(1) Chơi lại từ đầu\n(2) Thoát về Main Menu\nVui lòng chọn(1-2): ")
                if nxt == '1':
                    game_number = 1
                    current_hp, current_mot, current_cor = 50, 50, 50
                    break
                elif nxt == '2':
                    return
                else:
                    print("Lựa chọn không hợp lệ.")

if __name__ == "__main__":
    main_menu()