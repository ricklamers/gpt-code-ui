import { useState, useEffect } from "react";

import FormControl from '@mui/material/FormControl';
import FileOpenIcon from '@mui/icons-material/FileOpen';
import FolderOpenIcon from '@mui/icons-material/FolderOpen';
import DriveFolderUploadIcon from '@mui/icons-material/DriveFolderUpload';
import Alert from '@mui/material/Alert';
import Dialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
import DialogContent from '@mui/material/DialogContent';
import TextField from '@mui/material/TextField';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemAvatar from '@mui/material/ListItemAvatar';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemText from '@mui/material/ListItemText';
import Avatar from '@mui/material/Avatar';
import useLocalStorage from "use-local-storage";
import Config from "../config";


export type FoundryItem = {
    name: string;
    absolute_path: string;
    rid: string;
}

export type FoundryDir = {
    self: FoundryItem;
    parent: FoundryItem,
    children: FoundryItem[],
}


export default function Foundry(props: {
  onSelectFoundryDataset: (name: string) => void; }
) {
  const [foundryDialogOpen, setFoundryDialogOpen] = useState(false);
  const [foundryFolder, setFoundryFolder] = useLocalStorage<string | undefined>('foundryFolder', undefined);
  const [foundryDir, setFoundryDir] = useState<FoundryDir | undefined>(undefined);

  const getFoundryDir = async (folder: string | undefined) => {
    try {
      const params = folder != undefined ? new URLSearchParams({folder: folder}) : '';
      const response = await fetch(`${Config.WEB_ADDRESS}/foundry_files?${params}`);

      if (response.ok) {
        const json = await response.json();
        const fd: FoundryDir = json;
        if (folder == undefined) {
          setFoundryFolder(fd.self.absolute_path);
        }
        setFoundryDir(fd);
      } else {
        setFoundryDir(undefined);
      }
    } catch (e) {
      console.error(e);
      setFoundryDir(undefined);
    }
  };

  useEffect(() => {
    getFoundryDir(foundryFolder);
  }, [foundryFolder]);


  const handleFoundryDialogClose = (item: FoundryItem) => {
    if (isFolder(item.rid)) {
        setFoundryFolder(item.absolute_path);
    } else {
        props.onSelectFoundryDataset(item.rid);
        setFoundryDialogOpen(false);
    }
  };

  const isFolder = (rid: string) => {
    return rid.includes('ri.compass.main.folder');
  }

  return <>
        <Dialog open={foundryDialogOpen} onClose={() => setFoundryDialogOpen(false) } fullWidth maxWidth="sm">
          <DialogTitle>Select Foundry Dataset</DialogTitle>
          <DialogContent sx={{ display: 'flex', flexDirection: 'column' }}>
          <FormControl fullWidth>
            <TextField
              margin="dense"
              id="foundry-folder"
              label="Folder (RID or Path))"
              value = { foundryFolder }
              onChange = { e => { setFoundryFolder(e.target.value); }}
            />
          </FormControl>
            {foundryDir != undefined &&
              <List sx={{ pt: 0 }} dense>
                <ListItem disableGutters key={ foundryDir.parent.rid }>
                    <ListItemButton onClick={ () => handleFoundryDialogClose(foundryDir.parent) }>
                      <ListItemAvatar>
                        <Avatar sx={{ width: 32, height: 32 }}>
                          <DriveFolderUploadIcon />
                        </Avatar>
                      </ListItemAvatar>
                      <ListItemText primary={ '..' } />
                    </ListItemButton>
                </ListItem>

                {foundryDir.children.map((item) => (
                  <ListItem disableGutters key={ item.rid }>
                    <ListItemButton onClick={ () => handleFoundryDialogClose(item) }>
                      <ListItemAvatar>
                        <Avatar sx={{ width: 32, height: 32 }}>
                          { isFolder(item.rid) ? <FolderOpenIcon /> : <FileOpenIcon /> }
                        </Avatar>
                      </ListItemAvatar>
                      <ListItemText primary={ item.name } />
                    </ListItemButton>
                  </ListItem>
                ))}
              </List>
            }
            {foundryDir != undefined && foundryDir.children.length == 0 &&
              <Alert severity="warning">No datasets found in folder</Alert>
            }
            {foundryDir == undefined &&
              <Alert severity="error">Access to folder failed. Does it exist? Do you have access permissions?</Alert>
            }
          </DialogContent>
        </Dialog>

        <button type="button" onClick={ () => setFoundryDialogOpen(true) }>
            <FileOpenIcon />
        </button>
    </>
}
