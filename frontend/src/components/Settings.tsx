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
import Stack from '@mui/material/Stack';
import FormControlLabel from '@mui/material/FormControlLabel';
import Switch from '@mui/material/Switch';


export default function Settings(props: {
  models: Array<{ name: string; displayName: string }>;
  selectedModel: string;
  onSelectModel: (val: string) => void;
  toggledOptions: string[];
  onToggledOptions: (val: string[]) => void;
  showCode: boolean;
  onShowCode: (val: boolean) => void;
}) {
  const options: Array<{ name: string; displayName: string }> = [
    {name: 'svg', displayName: 'Vector Graphics'},
  ];

  const models = props.models;
  const selectedModel = props.selectedModel;
  const onSelectModel = props.onSelectModel;

  useEffect(() => {
    if (models.length) {
        if (undefined === models.find(e => e.name === selectedModel)) {
          onSelectModel(models[0].name);
        } else {
          onSelectModel(selectedModel);
        }
      }
  }, [models, selectedModel, onSelectModel]);

  return (
    <>
          <Stack direction="column" spacing={0}>
            <label className="header">Settings</label>
            <Stack direction="column" spacing={1}>
            <FormControlLabel
              control={
                <Switch
                  checked={props.showCode}
                  onChange={(_ev, checked) => {props.onShowCode(checked)} }
                  inputProps={{ 'aria-label': 'controlled' }}
                />}
              label="Show Python Code"
            />
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
            </Stack>
          </Stack>
    </>
  );
}
