import React, { Component } from 'react';
import './App.css';
import Container from '@material-ui/core/Container';
import List from '@material-ui/core/List';
import ListItem from '@material-ui/core/ListItem';
import ListItemText from '@material-ui/core/ListItemText';
import Grid from '@material-ui/core/Grid';

function ListItemLink(props) {
  return <ListItem button component="a" {...props} />;
}

class App extends Component {

  render() {
    const links = this.props.srvs.map(
        (dt) =>
            <ListItemLink href={"/" + dt.host}>
                <ListItemText primary={dt.name} secondary={dt.desc}/>
            </ListItemLink>
    );

    return (
      <div className="App">
        <Container maxWidth="sm">
          <Grid container spacing={5}>
            <List component="nav" aria-label="url short">
              {links}
            </List>
          </Grid>
        </Container>
      </div>
    );
  }
}

export default App;
