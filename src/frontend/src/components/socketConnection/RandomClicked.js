import React, { useCallback, useEffect } from "react";
import { useSocket } from "../../socket/SocketProvider";

function SocketRandomClicked(props) {
  const socket = useSocket();

  const setLines = useCallback(
    (lines) => {
      if (props.mode === "strategy_random") {
        socket.off("receive-random-simulation-design");
      }
      props.setLine(lines);
      props.setTriggerGetInput(true);
    },
    [props, socket]
  ); // eslint-disable-next-line

  useEffect(() => {
    if (socket == null) return;

    if (props.trigger) {
      props.setTrigger(false);

      if (props.mode === "strategy_random") {
        socket.emit("random-simulation-design", {
          mode: props.mode,
          name: props.name,
          assumptions: props.assumptions,
          guarantees: props.guarantees,
          inputs: props.inputs,
          outputs: props.outputs,
          iterations: props.number,
        });
        socket.on("receive-random-simulation-design", setLines);
      }
    }
  }, [socket, props, setLines]);

  return <></>;
}

export default SocketRandomClicked;
