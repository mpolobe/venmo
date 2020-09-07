import React, { useEffect, useState } from 'react';
import { usePromiseTracker } from 'react-promise-tracker';
import { trackPromise } from 'react-promise-tracker';
import Loader from 'react-loader-spinner';
import { baseUrl } from '../config';
import { useSelector } from 'react-redux';
import '../styles/feed.css';
import Transaction from './Transaction';

const Feed = () => {
  const [transactionsData, setTransactionsData] = useState(null)
  const [tab, setTab] = useState("public")
  const currentUserId = useSelector(state => state.authentication.user.id)
  const { promiseInProgress } = usePromiseTracker();
  console.log("FEED");

  useEffect(() => {
    const fetchData = async () => {
      if (tab === "public") {
        const result = await trackPromise(fetch(`${baseUrl}/transaction/public`));
        if (result.ok) {
          const resultJSON = await result.json();
          setTransactionsData(resultJSON.data);
        }
      }
      else if (tab === "friends") {
        const result = await trackPromise(fetch(`${baseUrl}/transaction/${currentUserId}/friends`));
        if (result.ok) {
          const resultJSON = await result.json();
          setTransactionsData(resultJSON.data);
        }
      }
      else if (tab === "mine") {
        const result = await trackPromise(fetch(`${baseUrl}/transaction/${currentUserId}`));
        if (result.ok) {
          const resultJSON = await result.json();
          setTransactionsData(resultJSON.data);
        }
      }
    };
    fetchData();
  }, [currentUserId, tab]);

  if (!transactionsData){
    return null;
  }
  
  const LoadingIndicator = () => {
    return (
      <div style={{ width: "100%", height: "100", display: "flex", justifyContent: "center", alignItems: "center" }}>
        <Loader type="Rings" color="#00BFFF" height={80} width={80} />
      </div>
    )
  }
  
  return (
    <div className="feed">
      <div className="feed__tabs">
        <button className={tab === "public" ? "pressed" : ""} onClick={() => setTab("public")}>PUBLIC</button>
        <button className={tab === "friends" ? "pressed" : ""} onClick={() => setTab("friends")}>FRIENDS</button>
        <button className={tab === "mine" ? "pressed" : ""} onClick={() => setTab("mine")}>MINE</button>
      </div>
      {promiseInProgress 
        ? <LoadingIndicator/> 
        : transactionsData.map((t, index) => <Transaction key={t.id} transaction={t} audience={tab} index={index} transactionsData={transactionsData} newTransactionsData={transactionsData => setTransactionsData(transactionsData)} />)}
    </div>
  );
}

export default Feed;
