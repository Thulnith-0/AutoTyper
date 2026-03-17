# pyre-ignore-all-errors
import pyautogui # type: ignore
import threading
import time
import random
from typing import Callable, Dict, Any

class TypingEngine:
    TYPO_MAP = {
        'a': ['s', 'q', 'z'], 'b': ['v', 'n', 'h'], 'c': ['v', 'x', 'd'], 'd': ['s', 'f', 'e', 'c'],
        'e': ['w', 'r', 'd', 's'], 'f': ['d', 'g', 'r', 'v'], 'g': ['f', 'h', 't', 'b'], 'h': ['g', 'j', 'y', 'n'],
        'i': ['u', 'o', 'k'], 'j': ['h', 'k', 'u', 'm'], 'k': ['j', 'l', 'i'], 'l': ['k', 'o', 'p'],
        'm': ['n', 'k', 'j'], 'n': ['b', 'm', 'j'], 'o': ['i', 'p', 'l'], 'p': ['o', 'l'],
        'q': ['w', 'a'], 'r': ['e', 't', 'f'], 's': ['a', 'd', 'w'], 't': ['r', 'y', 'g', 'f'],
        'u': ['y', 'i', 'j'], 'v': ['c', 'b', 'f'], 'w': ['q', 'e', 's'], 'x': ['z', 'c', 's'],
        'y': ['t', 'u', 'h'], 'z': ['a', 'x', 's'],
        ' ': ['v', 'b', 'n', 'c', 'm'] 
    }

    def __init__(self, callbacks: Dict[str, Callable[..., Any]]):
        """
        callbacks is a dict expected to have:
        - update_status: func(msg, color)
        - update_time_left: func(seconds_rem)
        - finish_typing: func(msg, color)
        """
        self.callbacks: Dict[str, Callable[..., Any]] = callbacks
        self.stop_typing: bool = False
        self.is_typing: bool = False

    def get_adjacent_key(self, char: str) -> str:
        lower_char = char.lower()
        if lower_char in self.TYPO_MAP:
            typo_char = random.choice(self.TYPO_MAP[lower_char])
            return typo_char.upper() if char.isupper() else typo_char
        return random.choice('abcdefghijklmnopqrstuvwxyz')

    def _simulate_mistake(self, char: str) -> float:
        wrong_char = self.get_adjacent_key(char)
        pyautogui.typewrite(wrong_char)
        m_delay1 = random.uniform(0.1, 0.3)
        time.sleep(m_delay1)
        pyautogui.press('backspace')
        m_delay2 = random.uniform(0.1, 0.2)
        time.sleep(m_delay2)
        return m_delay1 + m_delay2

    def _simulate_hesitation(self) -> float:
        h_delay = random.uniform(0.1, 0.4)
        time.sleep(h_delay)
        return h_delay

    def start(self, text: str, target_time: float, start_delay: int, use_mistakes: bool, use_pauses: bool, use_speed: bool, use_hesitation: bool) -> None:
        self.stop_typing = False
        self.is_typing = True
        
        thread = threading.Thread(
            target=self._typing_logic, 
            args=(text, target_time, start_delay, use_mistakes, use_pauses, use_speed, use_hesitation)
        )
        thread.daemon = True
        thread.start()

    def abort(self) -> None:
        self.stop_typing = True

    def _typing_logic(self, text: str, target_time: float, start_delay: int, use_mistakes: bool, use_pauses: bool, use_speed: bool, use_hesitation: bool) -> None:
        try:
            # Countdown
            for i in range(start_delay, 0, -1):
                if self.stop_typing:
                    break
                if 'update_status' in self.callbacks:
                    self.callbacks['update_status'](f"Starting in {i} seconds...", "#e67e22")
                time.sleep(1)

            if self.stop_typing:
                if 'finish_typing' in self.callbacks:
                    self.callbacks['finish_typing']("Aborted by user", "#e74c3c")
                self.is_typing = False
                return

            if 'update_status' in self.callbacks:
                self.callbacks['update_status']("Typing in progress... (Hands off!)", "#2ba84a")
            
            num_chars = len(text)
            if num_chars == 0:
                if 'finish_typing' in self.callbacks:
                    self.callbacks['finish_typing']("Finished (Empty text)", "#1f6aa5")
                self.is_typing = False
                return

            # Estimate overhead for delays inside the overall target time
            active_typing_time: float = float(target_time)
            if use_pauses:
                active_typing_time *= 0.85 
            if use_hesitation:
                active_typing_time *= 0.95 
            if use_mistakes:
                active_typing_time *= 0.90 
                
            start_time = time.time()
            burst_counter: int = 0
            accumulated_penalty: float = 0.0

            # Pre-calculate boolean conditions and penalty multipliers outside the loop
            do_mistakes = bool(use_mistakes)
            do_hesitation = bool(use_hesitation)
            do_speed = bool(use_speed)
            do_pauses = bool(use_pauses)

            # Pre-define syntactic characters to avoid tuple creation in loop
            hesitation_chars = {',', '.', '!', '?', ';'}
            rhythm_chars = {'.', ',', '!', '?', '\n'}

            for i, char in enumerate(text):
                if self.stop_typing:  # type: ignore
                    break
                
                # Update time remaining
                elapsed = time.time() - start_time
                rem = max(0.0, target_time - elapsed)
                if 'update_time_left' in self.callbacks:  # type: ignore
                    self.callbacks['update_time_left'](rem)  # type: ignore
                
                chars_left = num_chars - i
                
                # Dynamic Base Rate Calculation
                avg_delay: float = max(0.001, rem / chars_left) if chars_left > 0 else 0.001
                current_delay: float = avg_delay
                
                # 1. Mistake logic
                if do_mistakes and (random.random() < 0.02) and char.isalnum():
                    accumulated_penalty += self._simulate_mistake(char)  # type: ignore
                
                # 2. Hesitation logic
                if do_hesitation and (char.isupper() or char in hesitation_chars):
                    accumulated_penalty += self._simulate_hesitation()

                # 3. Type the character
                if char == '\n':
                    pyautogui.press('enter')
                elif char == '\t':
                    pyautogui.press('tab')
                else:
                    pyautogui.typewrite(char)

                # 4. Compute realistic typing rhythm around the current required average
                if do_speed:
                    current_delay = random.uniform(avg_delay * 0.4, avg_delay * 1.6)
                    if char in rhythm_chars:
                        current_delay += random.uniform(0.05, 0.2)
                    elif char == ' ':
                        current_delay += random.uniform(0.02, 0.08)
                
                # 5. Massive Human Pauses (Simulating "Reading" or checking notes)
                if do_pauses:
                    burst_counter += 1  # type: ignore[assignment]
                    if burst_counter > random.randint(20, 50): 
                        burst_counter = 0
                        max_pause = min(10.0, rem * 0.5) 
                        if max_pause > 1.0:
                            p_delay = random.uniform(1.0, max_pause)
                            current_delay += p_delay
                            accumulated_penalty += p_delay

                if accumulated_penalty > 0 and current_delay > 0.01:
                    reclaim = min(accumulated_penalty, current_delay * 0.3)
                    accumulated_penalty -= reclaim
                    current_delay -= reclaim

                time.sleep(max(0.001, current_delay))

            actual_time = time.time() - start_time
            if not self.stop_typing:  # type: ignore
                if 'update_time_left' in self.callbacks:  # type: ignore
                    self.callbacks['update_time_left'](0)  # type: ignore
                if 'finish_typing' in self.callbacks:  # type: ignore
                    self.callbacks['finish_typing'](f"Completed in {actual_time:.1f}s", "#2ba84a")  # type: ignore
            else:
                if 'finish_typing' in self.callbacks:  # type: ignore
                    self.callbacks['finish_typing']("Aborted by user", "#e74c3c")  # type: ignore

        except pyautogui.FailSafeException:
            self.stop_typing = True
            if 'update_time_left' in self.callbacks:
                self.callbacks['update_time_left'](0)
            if 'finish_typing' in self.callbacks:
                self.callbacks['finish_typing']("Aborted! (Mouse failsafe triggered)", "#e74c3c")
        except Exception as e:
            self.stop_typing = True
            if 'finish_typing' in self.callbacks:
                self.callbacks['finish_typing'](f"Error: {str(e)}", "#e74c3c")
        finally:
            self.is_typing = False
