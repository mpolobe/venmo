import React from 'react';
import { useSelector } from 'react-redux';
import { BrowserRouter, Switch, Route } from 'react-router-dom';
import LandingPage from './components/LandingPage.js'
import SignIn from './components/SignIn.js'
import SignUp from './components/SignUp.js'
import DevList from './components/DevList.js'
import HowZenmoWorks from './components/HowZenmoWorks.js'
import SignUpNotice from './components/SignUpNotice.js'
import DashBoard from './components/DashBoard.js'
import FriendsList from './components/FriendsList.js';

import { PrivateRoute } from './utilities/authUtils'


function App() {
  const needSignIn = useSelector(state => !state.authentication.token);

  // const [loaded, setLoaded] = useState(false);
  // const dispatch = useDispatch();

  // useEffect(() => {
  //   setLoaded(true);
  //   dispatch(loadToken());
  // }, [dispatch]);

  // if (!loaded) {
  //   return null;
  // }

  return (
    <BrowserRouter>
        <Switch>
            <Route path="/signup" exact component={SignUpNotice} />
            <Route path="/signup/email" exact component={SignUp} />
            <Route path="/signin" exact component={SignIn} />
            <Route path="/" exact component={LandingPage} />
            <Route path="/about/product" exact component={HowZenmoWorks} />
            <Route path="/about" exact component={DevList} />
            <PrivateRoute path="/friends" needSignIn={needSignIn} exact component={FriendsList} />
            <PrivateRoute path="/dashboard" needSignIn={needSignIn} exact component={DashBoard} />
        </Switch>
    </BrowserRouter>
  );
}

export default App;
