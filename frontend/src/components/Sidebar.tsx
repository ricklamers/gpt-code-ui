import "./Sidebar.css";
import { useState, useEffect } from "react";
import InputLabel from '@mui/material/InputLabel';
import Box from '@mui/material/Box';
import OutlinedInput from '@mui/material/OutlinedInput';
import Chip from '@mui/material/Chip';
import MenuItem from '@mui/material/MenuItem';
import FormControl from '@mui/material/FormControl';
import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import IconButton from '@mui/material/IconButton';
import CloseIcon from '@mui/icons-material/Close';
import CancelIcon from "@mui/icons-material/Cancel";
import CheckIcon from "@mui/icons-material/Check";
import ReactPlayer from 'react-player';
import ReactMarkdown from 'react-markdown';
import Select, { SelectChangeEvent } from '@mui/material/Select';
import logo from "../../public/assets/VM_VibrantMFilled09_Syellow_Sblue.svg";
import demo_video from "../../public/assets/CodeImpact.mp4";
import disclaimer from "../../public/assets/Disclaimer.md"


export default function Sidebar(props: {
  models: Array<{ name: string; displayName: string }>;
  selectedModel: string;
  onSelectModel: any;
  toggledOptions: string[];
  onToggledOptions: any;
}) {
  let [demoDialogOpen, setDemoDialogOpen] = useState(false);
  let [disclaimerDialogOpen, setDisclaimerDialogOpen] = useState(true);

  const options: Array<{ name: string; displayName: string }> = [
    {name: 'svg', displayName: 'Vector Graphics'},
  ];

  useEffect(() => {
    if (props.models.length) {
        if (undefined === props.models.find(e => e.name === props.selectedModel)) {
          props.onSelectModel(props.models[0].name);
        } else {
          props.onSelectModel(props.selectedModel);
        }
      }
  }, [props.models]);


  return (
    <>
      <Dialog
        open={demoDialogOpen}
        onClose={() => setDemoDialogOpen(false) }
        maxWidth={false}
      >
        <DialogContent sx={{ display: 'flex', flexDirection: 'column' }}>
          <FormControl fullWidth>
            <ReactPlayer
              url={demo_video}
              controls={true}
              width="90vw"
              height="min(50vw, 85vh)"
              playing
            />
          </FormControl>
        </DialogContent>
        <IconButton
          aria-label="close"
          onClick={ () => setDemoDialogOpen(false) }
          sx={{
            position: 'absolute',
            right: 8,
            top: 8,
            color: '#ccc',
          }}
        >
          <CloseIcon />
        </IconButton>
      </Dialog>

      <Dialog
        open={disclaimerDialogOpen}
        onClose={() => setDisclaimerDialogOpen(false) }
        maxWidth={false}
      >
        <DialogContent sx={{ display: 'flex', flexDirection: 'column' }}>
          <FormControl fullWidth>
            <ReactMarkdown children={disclaimer} />
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => {
            setDisclaimerDialogOpen(false);
            setDemoDialogOpen(true);
          }}>
            Demo Video
          </Button>
          <Button onClick={ () => setDisclaimerDialogOpen(false) } variant="contained">I understand</Button>
        </DialogActions>
        <IconButton
          aria-label="close"
          onClick={ () => setDisclaimerDialogOpen(false) }
          sx={{
            position: 'absolute',
            right: 8,
            top: 8,
            color: '#ccc',
          }}
        >
          <CloseIcon />
        </IconButton>
      </Dialog>

      <div className="sidebar">
        <div className="sidebarUpper">
          <div className="logo">
            <div className="wrapper">
              <div className="header">
                <img src={ logo } />
              </div>
              <div className="header">
                <p className="headline">Code</p>
                <p className="headline">Impact</p>
              </div>
            </div>
            <div className='github'>
                Built with ❤️ by the AI & Quantum Lab
            </div>
            <div className='github'>
                using&nbsp;<a href='https://github.com/ricklamers/gpt-code-ui'>GPT-Code UI - v{import.meta.env.VITE_APP_VERSION}</a>
            </div>
          </div>
          <div className="documentation">
            <label className="header">Documentation</label>
            <Button onClick={() => { setDisclaimerDialogOpen(true); }}>ReadMe</Button>
            <Button onClick={() => { setDemoDialogOpen(true); }}>Demo Video</Button>
          </div>
        </div>
        <div className="sidebarMiddle">
        </div>
        <div className="sidebarLower">
          <div className="settings">
            <label className="header">Settings</label>
            <FormControl fullWidth className="setting">
              <InputLabel id="options-select-label">Options</InputLabel>
              <Select
              labelId="options-select-label"
              id="options-select"
              multiple
              value={props.toggledOptions}
              defaultValue={props.toggledOptions}
              label="Options"
              onChange={(event: SelectChangeEvent<typeof props.toggledOptions>) => props.onToggledOptions(typeof event.target.value === 'string' ? event.target.value.split(',') : event.target.value)}
              input={<OutlinedInput id="select-multiple-chip" label="Chip" />}
              renderValue={(selected) => (
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                  {selected.map((value) => (
                    <Chip
                      key={value}
                      label={options.find(x => x.name === value)?.displayName}
                      onDelete={() => props.onToggledOptions(
                        props.toggledOptions.filter((item) => item !== value)
                      )
                    }
                    deleteIcon={
                      <CancelIcon
                        onMouseDown={(event) => event.stopPropagation()}
                      />
                    }
                    />
                  ))}
                </Box>
              )}
              >
              {options.map(option => {
                  return (
                  <MenuItem
                    key={option.name}
                    value={option.name}
                    sx={{ justifyContent: "space-between" }}
                  >
                      {option.displayName}
                      {props.toggledOptions.includes(option.name) ? <CheckIcon color="info" /> : null}
                  </MenuItem>
                  );
              })}
              </Select>
            </FormControl>
            <FormControl fullWidth className="setting">
              <InputLabel id="model-select-label">Model</InputLabel>
              <Select
              labelId="model-select-label"
              id="simple-select"
              value={props.selectedModel}
              defaultValue={props.selectedModel}
              label="Model"
              onChange={(event: SelectChangeEvent) => props.onSelectModel(event.target.value as string)}
              >
              {props.models.map(model => {
                  return (
                  <MenuItem value={model.name}>
                      {model.displayName}
                  </MenuItem>
                  );
              })}
              </Select>
            </FormControl>
          </div>
        </div>
      </div>
    </>
  );
}
