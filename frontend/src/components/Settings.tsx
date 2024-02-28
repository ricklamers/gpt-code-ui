import "./Settings.css";
import { useEffect } from "react";
import InputLabel from '@mui/material/InputLabel';
import Box from '@mui/material/Box';
import OutlinedInput from '@mui/material/OutlinedInput';
import Chip from '@mui/material/Chip';
import MenuItem from '@mui/material/MenuItem';
import FormControl from '@mui/material/FormControl';
import CancelIcon from "@mui/icons-material/Cancel";
import CheckIcon from "@mui/icons-material/Check";
import Select, { SelectChangeEvent } from '@mui/material/Select';

export default function Settings(props: {
  models: Array<{ name: string; displayName: string }>;
  selectedModel: string;
  onSelectModel: any;
  toggledOptions: string[];
  onToggledOptions: any;
}) {
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
    </>
  );
}
