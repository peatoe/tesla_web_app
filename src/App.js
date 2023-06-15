import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';
import logo from './8_bit_tesla.png';

function App() {
  const [vehicleInfo, setVehicleInfo] = useState({});
  const [errorMessage, setErrorMessage] = useState('');
  const [refreshStatus, setRefreshStatus] = useState(null);

  const getVehicleInfo = async () => {
    setRefreshStatus('Data is being refreshed...');
    try {
      const response = await axios.get(' http://127.0.0.1:5000/api/vehicle');
      setVehicleInfo(response.data);
      setRefreshStatus('Data refresh successful');
      setErrorMessage('');
    } catch (error) {
      setErrorMessage(error.response ? error.response.data.error : 'Server is not responding');
      setRefreshStatus('');
    }
  };

  const startClimate = async () => {
    try {
      await axios.post(' http://127.0.0.1:5000/api/climate/start');
      getVehicleInfo();
    } catch (error) {
      setErrorMessage(error.response ? error.response.data.error : 'Server is not responding');
    }
  };

  const stopClimate = async () => {
    try {
      await axios.post(' http://127.0.0.1:5000/api/climate/stop');
      getVehicleInfo();
    } catch (error) {
      setErrorMessage(error.response ? error.response.data.error : 'Server is not responding');
    }
  };

  useEffect(() => {
    getVehicleInfo();
  }, []);

  const getClimateStatus = () => {
    if (vehicleInfo.Climate === 'on') {
      return 'On';
    } else if (vehicleInfo.Climate === 'off') {
      return 'Off';
    } else {
      return '-';
    }
  };

  return (
    <div className="app">
      <h1 className="title">
        <img src={logo} alt="Logo" className="logo" /> Tesla Controller
      </h1>

      <div className="info">
        <p>Vehicle: {vehicleInfo.Vehicle || '-'}</p>
        <p>Battery Level: {vehicleInfo['Battery Level'] || '-'}</p>
        <p>Charging: {vehicleInfo.Charging || '-'}</p>
        <p>Climate: {getClimateStatus()}</p>
        <p className={vehicleInfo['Vehicle Status'] === 'online' ? 'status-online' : 'status-offline'}>
          Vehicle Status: {vehicleInfo['Vehicle Status'] || '-'}
        </p>
      </div>

      <div className="button-box">
        <div className="buttons">
          <button onClick={getVehicleInfo}>Refresh Data</button>
          <p>{refreshStatus}</p>
          <button onClick={startClimate}>Start Climate</button>
          <button onClick={stopClimate}>Stop Climate</button>
        </div>
      </div>

      {errorMessage && <p className="error-message">{errorMessage}</p>}
    </div>
  );
}

export default App;
