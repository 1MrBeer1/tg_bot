import './App.css';
import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import LogInPage from './components/logInPage';
import Main from './components/main';
import Protector from './components/protector';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LogInPage />} />
        <Route path="/main" element={<Main/>} />
        <Route path="*" element={<Protector/>}/>
      </Routes>
    </Router>
  );
}

export default App;