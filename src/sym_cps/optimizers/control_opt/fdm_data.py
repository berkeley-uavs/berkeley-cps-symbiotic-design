import os
import re


class FDMData(object):
    def __init__(self, table_path, file_path=None):
        self._data = {}
        self._lines = []
        self._table_path = table_path

        if file_path is not None:
            self.read_input(file_path)

    @property
    def data(self):
        return self._data

    def read_input(self, file_path):
        part_names = set()
        with open(file_path, "r") as file:
            lines = file.readlines()
            for line in lines:
                ret = FDMData.parseLine(line)

                if ret is None:
                    self._lines.append(line)
                    continue

                part_name = ret["part_name"]
                index = ret["index"]
                prop_name = ret["prop_name"]
                val = ret["val"]

                # only extract control

                # no index
                if part_name == "control":
                    self._data[prop_name] = val
                else:
                    # process the fname
                    if prop_name == "prop_fname":
                        base_file_path = val.replace("'", "")
                        file_name = os.path.basename(base_file_path)
                        new_file_path = os.path.join(self._table_path, file_name)
                        # print(new_file_path)
                        line = f"  {part_name}({index})%{prop_name} = '{new_file_path}'\n"
                    self._lines.append(line)

        # print(self._data)

    def write_input(self, file_path):
        with open(file_path, "w") as file:
            for line in self._lines[:-1]:
                file.write(line)

            for prop_name, val in self._data.items():
                file.write(f"  control%{prop_name} = {val}\n")
            file.write("/\n")

    @staticmethod
    def parseLine(line):
        comment_sym = "!"
        eidx = line.find(comment_sym)
        line_no_comment = line[:eidx]

        ret = re.findall(r"(\w+)(\(([0-9]+)\))?\%(\w+)\s*=(.*)", line_no_comment)
        # match (name, (nid), nid, propname, val)
        if not ret:  # no match
            return None

        if len(ret) != 1:
            # print("Missing change line symbol")
            raise Exception

        m = list(ret[0])
        if m[2] == "":
            m[2] = None

        tokens = {
            "part_name": m[0],
            "index": m[2],
            "prop_name": m[3],
            "val": m[4],
        }
        # print("Tokens: ", tokens)
        return tokens


if __name__ == "__main__":
    table_path = r"D:\JWork\Agents\workspace\UAM_Workflows\Tables\PropData"
    file_path = os.path.join(os.path.dirname(__file__), "..", "fdm", "Trowel", "flightDyn.inp")
    data = FDMData(table_path, file_path)
    data.write_input("./fdm/test_input.inp")
