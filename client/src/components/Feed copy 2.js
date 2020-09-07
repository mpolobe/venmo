import React, { useEffect, useState } from 'react';
import { usePromiseTracker } from 'react-promise-tracker';
import { trackPromise } from 'react-promise-tracker';
import Loader from 'react-loader-spinner';
import { baseUrl } from '../config';
import { useSelector } from 'react-redux';
import '../styles/feed.css';
import Transaction from './Transaction';

const Feed = () => {
  const [transactions, setTransactions] = useState(null)
  const [tab, setTab] = useState("public")
  const currentUserId = useSelector(state => state.authentication.user.id)
  const { promiseInProgress } = usePromiseTracker();
  const [likesStatus, setLikesStatus] = useState(null);
  console.log("FEED");

  useEffect(() => {
    const fetchData = async () => {
      if (tab === "public") {
        const result = await trackPromise(fetch(`${baseUrl}/transaction/public`));
        if (result.ok) {
          const transactions = await result.json();
          setTransactions(transactions);
        }
      }
      else if (tab === "friends") {
        const result = await trackPromise(fetch(`${baseUrl}/transaction/${currentUserId}/friends`));
        if (result.ok) {
          const transactions = await result.json();
          setTransactions(transactions);
        }
      }
      else if (tab === "mine") {
        const result = await trackPromise(fetch(`${baseUrl}/transaction/${currentUserId}`));
        if (result.ok) {
          const transactions = await result.json();
          setTransactions(transactions);
        }
      }
    };
    fetchData();
  }, [currentUserId, tab]);
  console.log("TAB:", tab);
  
  
  if (!transactions){
    console.log("transactions NULL:", transactions);
    return null;
  }
  console.log("transactions:", transactions);
  const initialLikes = transactions.data.map(t => t.likers.filter(liker => liker.id === currentUserId).length === 1);
  console.log("initialLikes:", initialLikes);
  setLikesStatus(initialLikes);
  console.log("likesStatus:", likesStatus);

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
      {/* {promiseInProgress ? <LoadingIndicator /> : transactions.data.map((r, index) => <Transaction key={r.id} transaction={r} audience={tab} index={index} likes={likesStatus} likesStatus={likesStatus => setLikesStatus(likesStatus)} />)} */}
    </div>
  );
}

export default Feed;
