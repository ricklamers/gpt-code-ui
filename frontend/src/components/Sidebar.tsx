import "./Sidebar.css";
import InputLabel from '@mui/material/InputLabel';
import MenuItem from '@mui/material/MenuItem';
import FormControl from '@mui/material/FormControl';
import Select, { SelectChangeEvent } from '@mui/material/Select';
import logo from "../../public/assets/VM_VibrantMFilled09_Syellow_Sblue.svg";

export default function Sidebar(props: {
  models: Array<{ name: string; displayName: string }>;
  selectedModel: string;
  onSelectModel: any;
}) {
  return (
    <>
      <div className="sidebar">
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
        <div className="settings">
            <label className="header">Settings</label>
            <FormControl fullWidth>
              <InputLabel id="model-select-label">Model</InputLabel>
              <Select
              labelId="model-select-label"
              id="simple-select"
              value={props.selectedModel}
              label="Model"
              onChange={(event: SelectChangeEvent) => props.onSelectModel(event.target.value as string)}
              >
              {props.models.map((model, index) => {
                  return (
                  <MenuItem key={index} value={model.name}>
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
