import os
import json

class Efficiency_Calculator():
    def __init__(self) -> None:
        self.path = './output/'
        self.results = {}
        self.weight = 1.2
    
    def count_keys(self, keys, count_type):
        count = 0
        for key in keys:
            if key["interact_type"] == count_type:
                count += 1
        return count

    def recalc_cps(self, keys):
        total_time = 0
        press_count = 0
        
        for key in keys:
            try:
                if key['time_hovered'] >= 3:
                    total_time += 3
                else:
                    total_time += key["time_hovered"]
            except:
                pass
            if key["interact_type"] == 'pressed':
                press_count += 1
        return press_count / total_time 

    def calc(self, data) -> dict:
        temp = {}
        for key in data.keys():
            if "Run " in key:
                run_result = {}
                run_result["mode"] = data[key]["mode"]
                run_result["final_length"] = len(data[key]["submitted_text"])
                run_result["h_keys"] = self.count_keys(data[key]["interacted_keys"], "hovered")
                run_result["weight"] = self.weight
                run_result["cps"] = self.recalc_cps(data[key]["interacted_keys"])
                run_result["efficiency"] = run_result["final_length"] / run_result["h_keys"] + run_result["weight"] * run_result["cps"]
                temp[str(key)] = run_result
                #print(temp[key])
        return temp
    
    def load_file(self, path) -> dict:
        file = open(path)
        return json.load(file)

    def save_results(self):
        with open('results' + '.json', 'w') as convert_file:
            convert_file.write(json.dumps(
                self.results, indent=4, default=str))

    def process_all(self):
        c = 0
        for filename in os.listdir(self.path):
            f = os.path.join(self.path, filename)
            # checking if it is a file
            if os.path.isfile(f):
                print(f)
                data = self.load_file(f)
                run_name = data["user_id"] + '_' + str(c)
                self.results[run_name] = self.calc(data)
                c += 1
        
        self.save_results()


calc = Efficiency_Calculator()

calc.process_all()
