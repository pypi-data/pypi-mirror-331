import pandas as pd
import numpy as np
from dataclasses import dataclass
import pickle
from pathlib import Path
import fire
from importlib.resources import files
from scipy.spatial import KDTree



@dataclass
class RLmodel_small:
    sma_05: float
    sma_07: float
    sma_25: float
    sma_compare: int
    is_short: int

    model_file_path: str = f'{Path(__file__).resolve().parent}/small_q_table.npy'
    state_index_file: str = f'{Path(__file__).resolve().parent}/small_state_to_index.npy'

    def load_qtable(self):
        with open(self.model_file_path, "rb") as f:
            q_table = np.load(f)
        return q_table

    def load_state_index(self):
        with open(self.state_index_file, "rb") as f:
            state_to_index = np.load(f, allow_pickle=True).item()
        return state_to_index

    def load_action_mapping(self):
        action_mapping = {"go_long": 0, "go_short": 1, "do_nothing": 2}
        return action_mapping

    def prep_state(self):
        state = np.array([[self.sma_05, self.sma_07, self.sma_25, self.sma_compare, self.is_short]])
        if not np.all(np.isfinite(state)):
            state = np.nan_to_num(state, nan=0.0, posinf=0.0, neginf=0.0)
        return state
    
    def predict_action(self):
        state = self.prep_state()
        loaded_qtable = self.load_qtable()
        loaded_state_to_index = self.load_state_index()
        loaded_mapping = self.load_action_mapping()


        state_tuple = tuple(state.flatten())
        state_index = loaded_state_to_index.get(state_tuple, -1)
        if not state_index == -1:
            try:
                q_values = loaded_qtable[state_index]
            except ValueError as e:
                print(e)
        else:
            # Create a KDTree from the states in the loaded_state_to_index mapping
            state_tuples = list(loaded_state_to_index.keys())
            kdtree = KDTree(state_tuples)

            # Find the nearest neighbor to the current state
            distance, index = kdtree.query(state.flatten())
            nearest_state_tuple = state_tuples[index]
            new_state_index = loaded_state_to_index[nearest_state_tuple]
            q_values = loaded_qtable[new_state_index]
            #raise ValueError("State not found in the state index mapping.")
        best_action_index = np.argmax(q_values)
        
        action = [action for action, index in loaded_mapping.items() if index == best_action_index][0]
        
        results_dict = {
            "raw_state": state,
            "state_tuple": state_tuple,
            "best_action_index": best_action_index,
            "action": action
        }
        return results_dict

@dataclass
class RLmodel_large:
    opening: float
    high: float
    ema_26: float
    ema_12: float
    low: float
    mean_grad_hist: float
    close: float
    volume: float
    sma_25: float
    long_jcrosk: float
    short_kdj: int
    sma_compare: int
    ask: float
    bid: float
    is_short: int

    model_file_path: str = f'{Path(__file__).resolve().parent}/large_q_table.npy'
    state_index_file: str = f'{Path(__file__).resolve().parent}/large_state_to_index.npy'

    def load_qtable(self):
        with open(self.model_file_path, "rb") as f:
            q_table = np.load(f)
        return q_table

    def load_state_index(self):
        with open(self.state_index_file, "rb") as f:
            state_to_index = np.load(f, allow_pickle=True).item()
        return state_to_index

    def load_action_mapping(self):
        action_mapping = {"go_long": 0, "go_short": 1, "do_nothing": 2}
        return action_mapping

    def prep_state(self):
        state = np.array([[self.opening, self.high, \
                          self.ema_26, self.ema_12, self.low, self.mean_grad_hist, \
                          self.close, self.volume, self.sma_25, self.long_jcrosk, \
                          self.short_kdj, self.sma_compare, self.ask, self.bid, self.is_short]]
                    )

        # Check for NaN or Inf values in the state
        if not np.all(np.isfinite(state)):
            state = np.nan_to_num(state, nan=0.0, posinf=0.0, neginf=0.0)

        return state
    
    def predict_action(self):
        state = self.prep_state()
        loaded_qtable = self.load_qtable()
        loaded_state_to_index = self.load_state_index()
        loaded_mapping = self.load_action_mapping()


        state_tuple = tuple(state.flatten())
        state_index = loaded_state_to_index.get(state_tuple, -1)
        if not state_index == -1:
            try:
                q_values = loaded_qtable[state_index]
            except ValueError as e:
                print(e)
        else:
            # Create a KDTree from the states in the loaded_state_to_index mapping
            state_tuples = list(loaded_state_to_index.keys())
            kdtree = KDTree(state_tuples)

            # Find the nearest neighbor to the current state
            distance, index = kdtree.query(state.flatten())
            nearest_state_tuple = state_tuples[index]
            new_state_index = loaded_state_to_index[nearest_state_tuple]
            q_values = loaded_qtable[new_state_index]
            #raise ValueError("State not found in the state index mapping.")
        best_action_index = np.argmax(q_values)
        
        action = [action for action, index in loaded_mapping.items() if index == best_action_index][0]
        
        results_dict = {
            "raw_state": state,
            "state_tuple": state_tuple,
            "best_action_index": best_action_index,
            "action": action
        }
        return results_dict

@dataclass
class RLmodel_bids:
    ask: float
    bid: float
    sma_compare: int
    is_short: int

    model_file_path: str = f'{Path(__file__).resolve().parent}/bids_q_table.npy'
    state_index_file: str = f'{Path(__file__).resolve().parent}/bids_state_to_index.npy'

    def load_qtable(self):
        with open(self.model_file_path, "rb") as f:
            q_table = np.load(f)
        return q_table

    def load_state_index(self):
        with open(self.state_index_file, "rb") as f:
            state_to_index = np.load(f, allow_pickle=True).item()
        return state_to_index

    def load_action_mapping(self):
        action_mapping = {"go_long": 0, "go_short": 1, "do_nothing": 2}
        return action_mapping

    def prep_state(self):
        state = np.array([[self.ask, self.bid, self.sma_compare, self.is_short]])

        # Check for NaN or Inf values in the state
        if not np.all(np.isfinite(state)):
            state = np.nan_to_num(state, nan=0.0, posinf=0.0, neginf=0.0)

        return state
    
    def predict_action(self):
        state = self.prep_state()
        loaded_qtable = self.load_qtable()
        loaded_state_to_index = self.load_state_index()
        loaded_mapping = self.load_action_mapping()


        state_tuple = tuple(state.flatten())
        state_index = loaded_state_to_index.get(state_tuple, -1)
        if not state_index == -1:
            try:
                q_values = loaded_qtable[state_index]
            except ValueError as e:
                print(e)
        else:
            # Create a KDTree from the states in the loaded_state_to_index mapping
            state_tuples = list(loaded_state_to_index.keys())
            kdtree = KDTree(state_tuples)

            # Find the nearest neighbor to the current state
            distance, index = kdtree.query(state.flatten())
            nearest_state_tuple = state_tuples[index]
            new_state_index = loaded_state_to_index[nearest_state_tuple]
            q_values = loaded_qtable[new_state_index]
            #raise ValueError("State not found in the state index mapping.")
        best_action_index = np.argmax(q_values)
        
        action = [action for action, index in loaded_mapping.items() if index == best_action_index][0]
        
        results_dict = {
            "raw_state": state,
            "state_tuple": state_tuple,
            "best_action_index": best_action_index,
            "action": action
        }
        return results_dict


def main_small(sma_05: float, sma_07: float, sma_25: float, sma_compare: int, is_short: int) -> dict:
    try:
        rl_model = RLmodel_small(
            sma_05,
            sma_07,
            sma_25,
            sma_compare,
            is_short
        )

        return rl_model.predict_action().get("action")
    except Exception as e:
        print(e)

def main_large(opening, high, ema_26, ema_12, low,
         mean_grad_hist, close, volume, sma_25, long_jcrosk,
         short_kdj, sma_compare, ask, bid, is_short
        ) -> dict:
    try:
        rl_model = RLmodel_large(
            opening,
            high,
            ema_26,
            ema_12,
            low,
            mean_grad_hist,
            close,
            volume,
            sma_25,
            long_jcrosk,
            short_kdj,
            sma_compare,
            ask,
            bid,
            is_short
        )

        return rl_model.predict_action().get("action")
    except Exception as e:
        print(e)

def main_bids(ask: float, bid: float, sma_compare: int, is_short: int) -> dict:
    try:
        rl_model = RLmodel_bids(
            ask,
            bid,
            sma_compare,
            is_short
        )

        return rl_model.predict_action().get("action")
    except Exception as e:
        print(e)

def main(mode: str, *args):
    if mode == "small":
        # Ensure the correct number of arguments are provided
        if len(args) != 5:
            print("Error: 'small' mode requires 5 arguments: sma_05, sma_07, sma_25, sma_compare, is_short")
            return

        # Convert arguments to the correct types
        try:
            sma_05 = float(args[0])
            sma_07 = float(args[1])
            sma_25 = float(args[2])
            sma_compare = int(args[3])
            is_short = int(args[4])
        except ValueError as e:
            print(f"Error: Invalid argument type. Expected floats and ints. Details: {e}")
            return

        # Call the main_small function with the converted arguments
        result = main_small(sma_05, sma_07, sma_25, sma_compare, is_short)

        return result

    elif mode == "large":
        # Ensure the correct number of arguments are provided
        if len(args) != 13:
            print("Error: 'large' mode requires 13 arguments: opening, high, ema_26, ema_12, low, "
                  "mean_grad_hist, close, volume, sma_25, long_jcrosk, short_kdj, sma_compare, ask, bid, is_short")
            return

        # Convert arguments to the correct types
        try:
            opening = float(args[0])
            high = float(args[1])
            ema_26 = float(args[2])
            ema_12 = float(args[3])
            low = float(args[4])
            mean_grad_hist = float(args[5])
            close = float(args[6])
            volume = float(args[7])
            sma_25 = float(args[8])
            long_jcrosk = int(args[9])
            short_kdj = int(args[10])
            sma_compare = int(args[11])
            ask = float(args[12])
            bid = float(args[13])
            is_short = int(args[14])
        except ValueError as e:
            print(f"Error: Invalid argument type. Expected floats and ints. Details: {e}")
            return

        # Call the main_large function with the converted arguments
        result = main_large(opening, high, ema_26, ema_12, low, mean_grad_hist, close,
                            volume, sma_25, long_jcrosk, short_kdj, sma_compare, ask, bid, is_short)
        return result

    elif mode == "bids":
        # Ensure the correct number of arguments are provided
        if len(args) != 4:
            print("Error: 'bids' mode requires 5 arguments: bid, ask, sma_compare, is_short")
            return

        # Convert arguments to the correct types
        try:
            bid = float(args[0])
            ask = float(args[1])
            sma_compare = int(args[2])
            is_short = int(args[3])
        except ValueError as e:
            print(f"Error: Invalid argument type. Expected floats and ints. Details: {e}")
            return

        # Call the main_small function with the converted arguments
        result = main_bids(ask, bid, sma_compare, is_short)

        return result

    else:
        print(f"Invalid mode: {mode}. Use 'small' or 'large'.")

if __name__ == "__main__":
    fire.Fire(main)