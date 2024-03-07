import "./Kernel.css";
import { WaitingStates } from "./Chat";
import Button from '@mui/material/Button';
import Typography from '@mui/material/Typography';
import Stack from '@mui/material/Stack';
import DeleteIcon from '@mui/icons-material/Delete';
import CancelIcon from '@mui/icons-material/Cancel';
import RestartAltIcon from '@mui/icons-material/RestartAlt';
import NewReleasesIcon from '@mui/icons-material/NewReleases';
import HourglassBottomIcon from '@mui/icons-material/HourglassBottom';
import TerminalIcon from '@mui/icons-material/Terminal';
import EngineeringIcon from '@mui/icons-material/Engineering';
import FileUploadIcon from '@mui/icons-material/FileUpload';


function getIcon(state: WaitingStates) {
    // Animations adapted from https://codepen.io/nelledejones/pen/gOOPWrK
    switch (state) {
        case WaitingStates.SessionTimeout:
            return <NewReleasesIcon color="primary" sx={{
                animation: "hithere 1s ease infinite",
                "@keyframes hithere": {
                    "30%": { transform: "scale(1.2)" },
                    "40% 60%": { transform: "rotate(-20deg) scale(1.2)" },
                    "50%": { transform: "rotate(20deg) scale(1.2)" },
                    "70%": { transform: "rotate(0deg) scale(1.2)" },
                    "100%": { transform: "scale(1)" },
                  }
              }} />;
        case WaitingStates.WaitingForKernel:
            return <HourglassBottomIcon color="primary" sx={{
                animation: "spin 2s linear infinite",
                "@keyframes spin": {
                    "0%": { transform: "rotate(0deg)" },
                    "10%": { transform: "rotate(0deg)" },
                    "50%": { transform: "rotate(180deg)" },
                    "100%": { transform: "rotate(180deg)" },
                },
              }}/>;
        case WaitingStates.GeneratingCode:
            return <TerminalIcon color="primary" sx={{
                animation: "bounce-in-right 2s ease infinite",
                "@keyframes bounce-in-right": {
                    "0%": { opacity: "0", transform: "translateX(200px)" },
                    "60%": { opacity: "1", transform: "translateX(-30px)" },
                    "80%": { transform: "translateX(10px)" },
                    "100%": { transform: "translateX(0)" },
                  }
              }}/>;
        case WaitingStates.RunningCode:
            return <EngineeringIcon color="primary" sx={{
                animation: "pulse 1s infinite ease-in-out alternate",
                "@keyframes pulse": {
                    "from": { transform: "scale(0.8)" },
                    "to": { transform: "scale(1.2)" },
                  }
              }}/>;
        case WaitingStates.UploadingFile:
            return <FileUploadIcon color="primary" sx={{
                animation: "fade-in-up 2s ease infinite",
                  "@keyframes fade-un-down": {
                    "0%": {
                      opacity: "0",
                      transform: "translateY(0px)",
                    },
                    "100%": {
                      opacity: "1",
                      transform: "translateY(20px)",
                    },
                  }
              }}/>;
        case WaitingStates.Idle:
            return <></>;
    }
}

export default function Kernel(props: {
  state: WaitingStates;
  onClearChat: React.MouseEventHandler<HTMLButtonElement>;
  onInterruptKernel: React.MouseEventHandler<HTMLButtonElement>;
  onResetKernel: React.MouseEventHandler<HTMLButtonElement>;
}) {
  return (
    <>
          <Stack direction="column" spacing={0}>
            <Stack
              direction="row"
              justifyContent="space-between"
              alignItems="center"
            >
              <label className="header">Kernel</label>
              {getIcon(props.state)}
            </Stack>
            <Stack direction="column" spacing={1}>
                <Typography variant="caption">
                  {props.state}
                </Typography>
                <Button endIcon={<DeleteIcon color="primary" />} style={{justifyContent: "flex-end"}} onClick={props.onClearChat}>
                    Clear History
                </Button>
                <Button endIcon={<CancelIcon color="primary" />} style={{justifyContent: "flex-end"}} onClick={props.onInterruptKernel}>
                    Interrupt Execution
                </Button>
                <Button endIcon={<RestartAltIcon color="primary" />} style={{justifyContent: "flex-end"}} onClick={props.onResetKernel}>
                    Reset Kernel
                </Button>
            </Stack>
          </Stack>
    </>
  );
}
