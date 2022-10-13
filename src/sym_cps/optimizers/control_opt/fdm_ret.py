# Objective steady state speed is UVW world =     5.00    0.00    0.00 m/s =    11.18    0.00    0.00 miles per hour
#  Finished lmdif1 call; info =  1 (should be 1, 2 or 3; see MINPACK documentation)
#   UVW world, body         5.00000000     0.00000000     0.00000000     4.99901410    -0.00000000    -0.09928785
#   UVWdot, PQRdot         -0.00000002     0.00000000     0.00000010    -0.00000000     0.00000001     0.00000000
#   Pitch angle theta      -1.13782969
#   Controls  1 -  6        0.55127797     0.55124699     0.55138171     0.55141872
# Warning: at least one control channel is outside range of 0 < uc < 1, hence steady flight is unlikely.
#   Motor RPM  1 -  6    4043.17294808  4042.95689443  4043.89653616  4044.15467963
#   Motor Amps  1 -  6      5.79372874     5.79320052     5.79549796     5.79612920
#   Battery # 1 Current =   23.179 amps,  Time to 20% charge left =  372.8 s,  Flight distance =   1863.792 m

# target: extract distance, warning, and speed
class FDMResult:
    def __init__(self, file_path=None):
        self._path = file_path
        self.read()

    def read(self):
        self._steady_state = self.readSteadyState()
        self._metrics = self.readMetric()
        return self._steady_state, self._metrics

    @property
    def metrics(self):
        return self._metrics

    @property
    def fastest_trim_state(self):
        # print(len(self._steady_state))
        trim_states = {}
        for x, y, z, fail, distance in reversed(self._steady_state[:51]):
            # print(x)
            if not fail:
                trim_states["Level"] = x
                break
        for x, y, z, fail, distance in reversed(self._steady_state[51:101]):
            # print(x)
            if not fail:
                trim_states["Turning500"] = x
                break
        for x, y, z, fail, distance in reversed(self._steady_state[101:151]):
            # print(x)
            if not fail:
                trim_states["Turning300"] = x
                break
        return trim_states

    @property
    def fastest_turning_trim_state(self):
        fast_x = -1
        print(self._steady_state[51:102])
        for x, y, z, fail, distance in self._steady_state[51:102]:
            if not fail and x > fast_x:
                fast_x = x
            if x >= 50:
                break
        return fast_x

    @property
    def steady_state(self):
        return self._steady_state

    def get_metrics(self, name):
        if name not in self._metrics.keys():
            raise Exception(f"Key not found in metrics {name}")
        return self._metrics[name]

    def readSteadyState(self):
        state = 0
        results = []
        # 0  find speed
        # 1  find warning or get distance
        # 2  get distance after waring
        with open(self._path, "r") as file:
            for line in file.readlines():
                tokens = line.split()
                if len(tokens) > 0:
                    if state == 0:
                        x, y, z = self.readObjectiveSpeed(tokens)
                        if x is not None:
                            state = 1

                    elif state == 1:
                        fail = self.readWarning(tokens)
                        if fail is not None:
                            state = 2
                        else:
                            ret = self.readDistance(tokens)
                            if ret is not None:
                                fail = False
                                state = 0
                                results.append((x, y, z, fail, ret))
                    else:  # state == 2
                        ret = self.readDistance(tokens)
                        if ret is not None:
                            results.append((x, y, z, fail, ret))
                            state = 0
        # print(results)
        return results

    def readMetric(self):
        state = 0
        metrics = {}
        # 0, finding "#Metrics"
        # 1, storing metrics into a dictionary
        with open(self._path, "r") as file:
            for line in file.readlines():
                tokens = line.split()

                if not tokens:
                    state = 0
                    continue

                if state == 0:
                    if tokens[0] == "Final" and tokens[1] == "score":
                        metrics["Score"] = float(tokens[4])
                    if tokens[0] == "Final" and tokens[1] == "height":
                        metrics["Height"] = float(tokens[4])
                    if tokens[0] == "#Metrics":
                        state = 1
                elif state == 1:
                    metric_name = tokens[0]
                    num_list = [0.0] * (len(tokens) - 1)
                    for i, num_token in enumerate(tokens[1:]):
                        try:
                            num_list[i] = float(num_token)
                        except:
                            state = 0

                    metrics[metric_name] = num_list
        return metrics

    def readObjectiveSpeed(self, tokens):
        speedX = None
        speedY = None
        speedZ = None
        if tokens[0] == "Objective":
            speedX = float(tokens[8])
            speedY = float(tokens[9])
            speedZ = float(tokens[10])
        return speedX, speedY, speedZ

    def readWarning(self, tokens):
        if tokens[0] == "Warning:":
            # Unorth .ne. trim speed
            if len(tokens) >= 3 and tokens[1] == "Unorth" and tokens[2] == ".ne.":
                return 1
            elif len(tokens) >= 5 and tokens[1] == "at" and tokens[2] == "least" and tokens[3] == "one":
                # at least one value of UVWdot or PQRdot is large enough that steady flight is unlikely (not a trim state).
                if tokens[4] == "value":
                    return 2
                # at least one wing is loaded beyond max load, hence structural failure likely.
                elif tokens[4] == "wing":
                    return 3
                # at least one motor maximum current exceeded
                elif tokens[4] == "motor":
                    return 4
            #  Warning: battery voltage not high enough
            elif len(tokens) >= 2 and tokens[1] == "battery":
                return 5
            # Warning: wing can only rotate around X or Y axis.
            elif len(tokens) >= 2 and tokens[1] == "wing":
                return 6
            return True
        if tokens[0] == "Caution:":
            # Caution: at least one control channel is outside range of 0 < uc < 1, hence steady flight may be unlikely.
            if (
                len(tokens) >= 5
                and tokens[1] == "at"
                and tokens[2] == "least"
                and tokens[3] == "one"
                and tokens[4] == "control"
            ):
                return 7
            # Caution: current exceeds contiuous maximum for at least one of the batteries.
            if (
                len(tokens) >= 5
                and tokens[1] == "current"
                and tokens[2] == "exceeds"
                and tokens[3] == "contiuous"
                and tokens[4] == "maximum"
            ):
                return 8
            return True

        return None

    def readDistance(self, tokens):
        distance = None
        if tokens[0] == "Battery":
            if tokens[18] == "**********" or tokens[13] == "******":
                distance = 0
            else:
                distance = float(tokens[18])

        return distance


if __name__ == "__main__":
    reader = FDMResult("./fdm/flightDynOut.out")
    ret = reader.read()
    print(ret)
