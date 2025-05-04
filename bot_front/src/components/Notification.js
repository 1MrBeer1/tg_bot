import React, { useEffect } from 'react';
import './css/Notification.css'; 

const Notification = ({ message, show, onClose }) => {
  useEffect(() => {
    if (show) {
      const timer = setTimeout(() => {
        onClose();
      }, 3000);
      return () => clearTimeout(timer);
    }
  }, [show, onClose]);

  return (
    <div className={`notification ${show ? 'show' : ''}`}>
      {message}
    </div>
  );
};

export default Notification;