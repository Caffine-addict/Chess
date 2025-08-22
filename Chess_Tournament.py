import random
import math
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
class Player:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.score = 0.0
        self.tpr = 1000.0
        self.opponents = []
        self.has_had_bye = False
        self.is_withdrawn = False
    def __repr__(self):
        return f"Player({self.id}, '{self.name}', Score: {self.score}, TPR: {int(self.tpr)})"
class Tournament:
    def __init__(self):
        self.players = {}
        self.next_player_id = 1
        self.current_round = 0
        self.pairings = []
    def add_player(self, name):
        try:
            player_id = self.next_player_id
            self.players[player_id] = Player(player_id, name)
            self.next_player_id += 1
            print(f"{bcolors.OKGREEN}Success:{bcolors.ENDC} Added player '{name}' with ID {player_id}.")
        except Exception as e:
            print(f"{bcolors.FAIL}Error:{bcolors.ENDC} Could not add player. {e}")
    def withdraw_player(self, player_id):
        if player_id not in self.players:
            print(f"{bcolors.FAIL}Error:{bcolors.ENDC} Player with ID {player_id} not found.")
            return
        player = self.players[player_id]
        if player.is_withdrawn:
            print(f"{bcolors.WARNING}Info:{bcolors.ENDC} Player {player.name} is already withdrawn.")
        else:
            player.is_withdrawn = True
            print(f"{bcolors.OKGREEN}Success:{bcolors.ENDC} Player {player.name} has been withdrawn from the tournament.")
    def get_active_players(self):
        return [p for p in self.players.values() if not p.is_withdrawn]
    def pair_round(self):
        if self.current_round > 0 and self.pairings:
             print(f"{bcolors.FAIL}Error:{bcolors.ENDC} Cannot pair a new round until results for the current round are entered.")
             return False
        self.current_round += 1
        active_players = self.get_active_players()
        players_sorted = sorted(active_players, key=lambda p: (p.score, p.tpr), reverse=True)
        self.pairings = []
        paired_ids = set()
        bye_player = None
        if len(players_sorted) % 2 != 0:
            for player in reversed(players_sorted):
                if not player.has_had_bye:
                    bye_player = player
                    break
            if not bye_player:
                bye_player = players_sorted[-1]
            bye_player.score += 1.0
            bye_player.has_had_bye = True
            paired_ids.add(bye_player.id)
            print(f"{bcolors.OKBLUE}INFO:{bcolors.ENDC} {bye_player.name} receives a bye and 1 point.")
        players_to_pair = [p for p in players_sorted if p.id not in paired_ids]
        for i in range(len(players_to_pair)):
            player1 = players_to_pair[i]
            if player1.id in paired_ids:
                continue
            for j in range(i + 1, len(players_to_pair)):
                player2 = players_to_pair[j]
                if player2.id not in paired_ids and player2.id not in player1.opponents:
                    self.pairings.append((player1.id, player2.id))
                    paired_ids.add(player1.id)
                    paired_ids.add(player2.id)
                    player1.opponents.append(player2.id)
                    player2.opponents.append(player1.id)
                    break
        if len(self.pairings) == 0 and not bye_player:
            print(f"{bcolors.WARNING}Warning:{bcolors.ENDC} No valid pairings could be made.")
            self.current_round -= 1
            return False
        return True
    def record_results(self):
        if not self.pairings:
            print(f"{bcolors.FAIL}Error:{bcolors.ENDC} No pairings exist for the current round.")
            return
        print(f"\n--- {bcolors.HEADER}Enter Results for Round {self.current_round}{bcolors.ENDC} ---")
        for p1_id, p2_id in self.pairings:
            p1 = self.players[p1_id]
            p2 = self.players[p2_id]
            while True:
                try:
                    prompt = (f"Match: {bcolors.OKBLUE}{p1.name}{bcolors.ENDC} vs {bcolors.OKBLUE}{p2.name}{bcolors.ENDC}. "
                              f"Enter result (1 for {p1.name} win, 0 for {p2.name} win, 0.5 for draw): ")
                    result = input(prompt)
                    if result == '1':
                        p1.score += 1.0
                        p1.tpr += 50 + (p2.score * 10)
                        p2.tpr -= 50
                        break
                    elif result == '0':
                        p2.score += 1.0
                        p2.tpr += 50 + (p1.score * 10)
                        p1.tpr -= 50
                        break
                    elif result == '0.5':
                        p1.score += 0.5
                        p2.score += 0.5
                        if p1.score > p2.score:
                            p2.tpr += 25
                            p1.tpr -= 25
                        else:
                            p1.tpr += 25
                            p2.tpr -= 25
                        break
                    else:
                        print(f"{bcolors.FAIL}Invalid input.{bcolors.ENDC} Please enter 1, 0, or 0.5.")
                except ValueError:
                    print(f"{bcolors.FAIL}Invalid input.{bcolors.ENDC} Please enter a valid number.")
                except Exception as e:
                    print(f"{bcolors.FAIL}An error occurred: {e}{bcolors.ENDC}")
        print(f"\n{bcolors.OKGREEN}Success:{bcolors.ENDC} All results for Round {self.current_round} have been recorded.")
        self.pairings = []
    def print_standings(self):
        print(f"\n--- {bcolors.HEADER}{bcolors.BOLD}Tournament Standings after Round {self.current_round}{bcolors.ENDC} ---")
        all_players = list(self.players.values())
        standings = sorted(all_players, key=lambda p: (p.score, p.tpr, p.name), reverse=True)
        print(f"{'Rank':<5} {'ID':<5} {'Name':<20} {'Status':<12} {'Score':<8} {'TPR':<8}")
        print("-" * 60)
        for i, player in enumerate(standings):
            rank = i + 1
            status = "Withdrawn" if player.is_withdrawn else "Active"
            color = bcolors.FAIL if player.is_withdrawn else bcolors.OKGREEN
            print(f"{rank:<5} {player.id:<5} {player.name:<20} {color}{status:<12}{bcolors.ENDC} {player.score:<8.1f} {int(player.tpr):<8}")
        print("-" * 60)
    def reset_tournament(self):
        self.current_round = 0
        self.pairings = []
        for player in self.players.values():
            player.score = 0.0
            player.tpr = 1000.0
            player.opponents = []
            player.has_had_bye = False
        print(f"{bcolors.OKGREEN}Success:{bcolors.ENDC} Tournament has been reset. Scores and rounds are cleared.")
def print_main_menu():
    print(f"\n{bcolors.HEADER}--- Chess Tournament Menu ---{bcolors.ENDC}")
    print("1. Add Player")
    print("2. Withdraw Player")
    print("3. View Standings")
    print("4. Start Next Round & Generate Pairings")
    print("5. Enter Round Results")
    print("6. Reset Tournament")
    print("7. Exit")
    print("-" * 29)
def main():
    tournament = Tournament()
    tournament.add_player("Magnus")
    tournament.add_player("Hikaru")
    tournament.add_player("Fabiano")
    tournament.add_player("Anish")
    tournament.add_player("Alireza")
    while True:
        print_main_menu()
        choice = input("Enter your choice: ")
        if choice == '1':
            name = input("Enter player name: ")
            if name:
                tournament.add_player(name)
            else:
                print(f"{bcolors.FAIL}Error:{bcolors.ENDC} Player name cannot be empty.")
        elif choice == '2':
            try:
                player_id = int(input("Enter player ID to withdraw: "))
                tournament.withdraw_player(player_id)
            except ValueError:
                print(f"{bcolors.FAIL}Error:{bcolors.ENDC} Invalid ID. Please enter a number.")
        elif choice == '3':
            tournament.print_standings()
        elif choice == '4':
            if tournament.pair_round():
                print(f"\n--- {bcolors.HEADER}Pairings for Round {tournament.current_round}{bcolors.ENDC} ---")
                for p1_id, p2_id in tournament.pairings:
                    p1_name = tournament.players[p1_id].name
                    p2_name = tournament.players[p2_id].name
                    print(f"{bcolors.OKBLUE}{p1_name}{bcolors.ENDC} vs {bcolors.OKBLUE}{p2_name}{bcolors.ENDC}")
                print("-" * 30)
        elif choice == '5':
            tournament.record_results()
        elif choice == '6':
            confirm = input(f"{bcolors.WARNING}Are you sure you want to reset all scores and rounds? (yes/no): {bcolors.ENDC}").lower()
            if confirm == 'yes':
                tournament.reset_tournament()
            else:
                print("Reset cancelled.")
        elif choice == '7':
            print("Exiting tournament manager. Goodbye!")
            break
        else:
            print(f"{bcolors.FAIL}Invalid choice.{bcolors.ENDC} Please select a valid option.")
if __name__ == "__main__":
    main()
