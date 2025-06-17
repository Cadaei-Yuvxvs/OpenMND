import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
} from '@mui/material';
import { Link, useLocation } from 'react-router-dom';
import { styled } from '@mui/material/styles';

const StyledAppBar = styled(AppBar)(({ theme }) => ({
  backgroundColor: theme.palette.primary.main,
  boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
}));

const NavButton = styled(Button)<{ active?: boolean }>(({ theme, active }) => ({
  color: 'white',
  margin: '0 8px',
  padding: '8px 16px',
  borderRadius: '4px',
  backgroundColor: active ? 'rgba(255,255,255,0.1)' : 'transparent',
  '&:hover': {
    backgroundColor: 'rgba(255,255,255,0.2)',
  },
}));

const Navbar = () => {
  const location = useLocation();

  return (
    <StyledAppBar position="static">
      <Toolbar>
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          OpenMND Research Intelligence
        </Typography>
        <Box sx={{ display: 'flex' }}>
          <NavButton
            component={Link}
            to="/"
            active={location.pathname === '/'}
          >
            Dashboard
          </NavButton>
          <NavButton
            component={Link}
            to="/research"
            active={location.pathname === '/research'}
          >
            Research Database
          </NavButton>
          <NavButton
            component={Link}
            to="/analytics"
            active={location.pathname === '/analytics'}
          >
            Analytics
          </NavButton>
        </Box>
      </Toolbar>
    </StyledAppBar>
  );
};

export default Navbar;