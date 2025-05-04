import React, { useEffect, useState } from 'react';
import axios from 'axios';

function MyModelList() {
    const [data, setData] = useState([]);

    useEffect(() => {
        axios.get('/api/mymodel/')
            .then(response => {
                setData(response.data);
            })
            .catch(error => {
                console.error('Error fetching data:', error);
            });
    }, []);

    return (
        <ul>
            {data.map(item => (
                <li key={item.id}>{item.name}</li>
            ))}
        </ul>
    );
}

export default MyModelList;