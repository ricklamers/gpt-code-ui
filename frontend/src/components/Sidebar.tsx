import AssistantIcon from '@mui/icons-material/Assistant';

import "./Sidebar.css";
import { useState, useEffect } from "react";
import InputLabel from '@mui/material/InputLabel';
import Box from '@mui/material/Box';
import OutlinedInput from '@mui/material/OutlinedInput';
import Chip from '@mui/material/Chip';
import MenuItem from '@mui/material/MenuItem';
import FormControl from '@mui/material/FormControl';
import Select, { SelectChangeEvent } from '@mui/material/Select';

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
      <div className="sidebar">
        <div className="logo">
            <div className="wrapper">
              <div className="header">
                <AssistantIcon />
              </div>
              <div className="header">
                <p className="headline">Code</p>
                <p className="headline">Impact</p>
              </div>
            </div>
            <div className='github'>
                Built with ❤️
            </div>
            <div className='github'>
                using&nbsp;<a href='https://github.com/ricklamers/gpt-code-ui'>GPT-Code UI - v{import.meta.env.VITE_APP_VERSION}</a>
            </div>
        </div>
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
                    <Chip key={value} label={options.find(x => x.name === value)?.displayName} />
                  ))}
                </Box>
              )}
              >
              {options.map(option => {
                  return (
                  <MenuItem value={option.name}>
                      {option.displayName}
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
    </>
  );
}
