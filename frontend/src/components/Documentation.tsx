import "./Documentation.css";
import { useState } from "react";
import FormControl from '@mui/material/FormControl';
import Button from '@mui/material/Button';
import Stack from '@mui/material/Stack';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import IconButton from '@mui/material/IconButton';
import CloseIcon from '@mui/icons-material/Close';
import ReactPlayer from 'react-player';
import ReactMarkdown from 'react-markdown';
import ReceiptLongIcon from '@mui/icons-material/ReceiptLong';
import VideoChatIcon from '@mui/icons-material/VideoChat';
import ListAltIcon from '@mui/icons-material/ListAlt';
// TODO: import demo_video from "../../public/assets/DemoVideo.mp4";
import disclaimer from "../../public/assets/Disclaimer.md"
import changelog from "../../public/assets/Changelog.md"


export default function Documentation() {
  let [demoDialogOpen, setDemoDialogOpen] = useState(false);
  let [disclaimerDialogOpen, setDisclaimerDialogOpen] = useState(true);
  let [changelogDialogOpen, setChangelogDialogOpen] = useState(false);

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
              // url={demo_video}
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
          <Button onClick={() => {
            setDisclaimerDialogOpen(false);
            setChangelogDialogOpen(true);
          }}>
            Recent Changes
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

      <Dialog
        open={changelogDialogOpen}
        onClose={() => setChangelogDialogOpen(false) }
        maxWidth={false}
      >
        <DialogContent sx={{ display: 'flex', flexDirection: 'column' }}>
          <FormControl fullWidth>
            <ReactMarkdown children={changelog} />
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={ () => setChangelogDialogOpen(false) } variant="contained">Close</Button>
        </DialogActions>
        <IconButton
          aria-label="close"
          onClick={ () => setChangelogDialogOpen(false) }
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

      <Stack direction="column" spacing={0}>
        <label className="header">Documentation</label>
        <Stack direction="column" spacing={1}>
            <Button endIcon={<ReceiptLongIcon color="primary" />} style={{justifyContent: "flex-end"}} onClick={() => { setDisclaimerDialogOpen(true); }}>ReadMe</Button>
            <Button endIcon={<VideoChatIcon color="primary" />} style={{justifyContent: "flex-end"}} onClick={() => { setDemoDialogOpen(true); }}>Demo Video</Button>
            <Button endIcon={<ListAltIcon color="primary" />} style={{justifyContent: "flex-end"}} onClick={() => { setChangelogDialogOpen(true); }}>Recent Changes</Button>
        </Stack>
      </Stack>
    </>
  );
}
