import {
  BrowserRouter as Router,
  Switch,
  Route,
} from "react-router-dom";
import { PrivateRoute } from "./components/PrivateRoute";
import Login from "./components/Login"
import Dashboard from "./components/Dashboard";
import Dumbledore from "./components/Dumbledore";
import { ProvideAuth } from "./hooks/use-auth";

function App() {
  return (
    <ProvideAuth>
      <Router>
        <Switch>
          <Route exact path={'/login'} component={Login}/>
          <PrivateRoute exact path={'/dumbledore'} component={Dumbledore}/>
          <Route path={'/'} component={Dashboard}/>
        </Switch>
      </Router>
    </ProvideAuth>
  );
}

export default App;
