# Networking/NetworkServiceImpl.py
import requests
from typing import Optional
from CoreDomainModel.Code import Code
from CoreDomainModel.EvaluationResult import EvaluationResult
from CoreDomainModel.GameVariant import GameVariant
from Networking.NetworkService import NetworkService


class NetworkServiceImpl(NetworkService):
    """Service for communicating with remote evaluation server."""

    def __init__(self, server_url: str = "http://127.0.0.1:8080", gamer_id: str = "player1"):
        self.server_url = server_url.rstrip('/')
        self.gamer_id = gamer_id
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.session.timeout = 5
        self.current_game_id: Optional[int] = None
        self.variant: Optional[GameVariant] = None

    def start_new_game(self, variant: GameVariant, secret_code: Code) -> Optional[str]:
        """
        Start a new game on the server and send secret code
        Returns None if server is not available (caller should use local evaluation)
        """
        try:
            secret_pegs = [peg.value for peg in secret_code.get_pegs()]

            payload = {
                "gameid": 0,
                "title": "Mastermind Game",
                "_comment": "Starting new game with secret code",
                "positions": variant.code_length,
                "colors": variant.color_count,
                "secret_code": secret_pegs
            }

            response = self.session.post(
                f"{self.server_url}/api/game",
                json=payload,
                timeout=5
            )

            if response.status_code == 200:
                data = response.json()
                self.current_game_id = str(data.get("gameid"))
                return self.current_game_id
            else:
                print(f"Server error: {response.status_code} - {response.text}")
                return None

        except requests.exceptions.Timeout:
            print(f"Server timeout: {self.server_url}")
            return None
        except requests.exceptions.ConnectionError:
            print(f"Server connection error: {self.server_url}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"Network error: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None

    def start_remote_game(self, variant: GameVariant) -> Optional[int]:
        """
        Start a new game on the server
        Server creates the secret code (value is empty string)
        Returns game_id if successful
        """
        try:
            self.variant = variant

            payload = {
                "gameid": 0,
                "gamerid": self.gamer_id,
                "positions": variant.code_length,
                "colors": variant.color_count,
                "value": ""
            }

            response = self.session.post(
                f"{self.server_url}/",
                json=payload,
                timeout=5
            )

            if response.status_code == 200:
                data = response.json()
                self.current_game_id = data.get("gameid")
                return self.current_game_id
            else:
                print(f"Server error: {response.status_code} - {response.text}")
                return None

        except requests.exceptions.Timeout:
            print(f"Server timeout: {self.server_url}")
            return None
        except requests.exceptions.ConnectionError:
            print(f"Server connection error: {self.server_url}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"Network error: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None

    def evaluate_guess(self, guess: Code) -> Optional[EvaluationResult]:
        """
        Evaluate a guess for the current game
        Returns None if server is not available (caller should handle)
        """
        if not self.current_game_id or not self.variant:
            print(f"[ERROR] NetworkService.evaluate_guess: game_id={self.current_game_id}, variant={self.variant}")
            return None

        try:
            guess_pegs = [peg.value for peg in guess.get_pegs()]
            value_str = "".join(str(p) for p in guess_pegs)

            payload = {
                "gameid": self.current_game_id,
                "gamerid": self.gamer_id,
                "positions": self.variant.code_length,
                "colors": self.variant.color_count,
                "value": value_str
            }

            response = self.session.post(
                f"{self.server_url}/",
                json=payload,
                timeout=5
            )

            if response.status_code == 200:
                data = response.json()

                value_response = data.get("value", "")

                if "," in value_response:
                    parts = value_response.split(",")
                    try:
                        black = int(parts[0].strip())
                        white = int(parts[1].strip()) if len(parts) > 1 else 0
                    except ValueError:
                        print(f"Invalid response format: {value_response}")
                        return None
                else:
                    print(f"Unexpected response format: {value_response}")
                    return None

                return EvaluationResult(
                    correct_position=black,
                    correct_color=white
                )
            elif response.status_code == 404:
                print("Error: Game not found (404)")
                return None
            else:
                print(f"Server error: {response.status_code} - {response.text}")
                return None

        except requests.exceptions.Timeout:
            print(f"Server timeout during evaluation")
            return None
        except requests.exceptions.ConnectionError:
            print(f"Server connection error during evaluation")
            return None
        except requests.exceptions.RequestException as e:
            print(f"Network error: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None
