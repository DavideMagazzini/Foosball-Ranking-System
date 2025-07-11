import React, { useState, useEffect, useRef } from 'react';
import { initializeApp } from 'firebase/app';
import { getAuth, signInAnonymously, signInWithCustomToken, onAuthStateChanged } from 'firebase/auth';
import { getFirestore, collection, doc, getDoc, setDoc, updateDoc, onSnapshot, query, where, addDoc, getDocs } from 'firebase/firestore';

// Main App component
const App = () => {
  const [db, setDb] = useState(null);
  const [auth, setAuth] = useState(null);
  const [userId, setUserId] = useState(null);
  const [players, setPlayers] = useState([]);
  const [newPlayerName, setNewPlayerName] = useState('');
  const [team1Players, setTeam1Players] = useState([]);
  const [team2Players, setTeam2Players] = useState([]);
  const [winner, setWinner] = useState('');
  const [message, setMessage] = useState('');
  const [showAddPlayerModal, setShowAddPlayerModal] = useState(false);
  const [showRecordGameModal, setShowRecordGameModal] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  // Elo rating constants
  const K_FACTOR = 32; // Maximum possible adjustment per game
  const INITIAL_SCORE = 1000; // Starting score for new players

  // Firebase initialization and authentication
  useEffect(() => {
    try {
      const appId = typeof __app_id !== 'undefined' ? __app_id : 'default-app-id';
      const firebaseConfig = JSON.parse(typeof __firebase_config !== 'undefined' ? __firebase_config : '{}');

      if (Object.keys(firebaseConfig).length === 0) {
        console.error("Firebase config is not defined. Please ensure __firebase_config is set.");
        setMessage("Error: Firebase configuration missing.");
        setIsLoading(false);
        return;
      }

      const app = initializeApp(firebaseConfig);
      const firestore = getFirestore(app);
      const firebaseAuth = getAuth(app);

      setDb(firestore);
      setAuth(firebaseAuth);

      const unsubscribeAuth = onAuthStateChanged(firebaseAuth, async (user) => {
        if (user) {
          setUserId(user.uid);
          console.log("Authenticated with UID:", user.uid);
        } else {
          // Sign in anonymously if no user is found and no custom token is provided
          try {
            if (typeof __initial_auth_token !== 'undefined' && __initial_auth_token) {
              await signInWithCustomToken(firebaseAuth, __initial_auth_token);
              console.log("Signed in with custom token.");
            } else {
              await signInAnonymously(firebaseAuth);
              console.log("Signed in anonymously.");
            }
          } catch (error) {
            console.error("Error signing in:", error);
            setMessage(`Authentication error: ${error.message}`);
          }
        }
        setIsLoading(false);
      });

      return () => unsubscribeAuth();
    } catch (error) {
      console.error("Error initializing Firebase:", error);
      setMessage(`Firebase initialization error: ${error.message}`);
      setIsLoading(false);
    }
  }, []);

  // Fetch players data in real-time
  useEffect(() => {
    if (!db || !userId) return;

    const playersCollectionRef = collection(db, `artifacts/${__app_id}/public/data/players`);
    const unsubscribePlayers = onSnapshot(playersCollectionRef, (snapshot) => {
      const playersData = snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
      setPlayers(playersData.sort((a, b) => b.score - a.score)); // Sort by score descending
    }, (error) => {
      console.error("Error fetching players:", error);
      setMessage(`Error loading players: ${error.message}`);
    });

    return () => unsubscribePlayers();
  }, [db, userId]);

  // Function to add a new player
  const addPlayer = async () => {
    if (!db || !userId) {
      setMessage("Database not ready or not authenticated.");
      return;
    }
    if (!newPlayerName.trim()) {
      setMessage("Player name cannot be empty.");
      return;
    }

    try {
      const playersCollectionRef = collection(db, `artifacts/${__app_id}/public/data/players`);
      // Check if player already exists
      const q = query(playersCollectionRef, where("name", "==", newPlayerName.trim()));
      const querySnapshot = await getDocs(q);
      if (!querySnapshot.empty) {
        setMessage("Player with this name already exists.");
        return;
      }

      await addDoc(playersCollectionRef, {
        name: newPlayerName.trim(),
        score: INITIAL_SCORE, // Initial Elo score
        createdAt: new Date(),
      });
      setMessage(`Player "${newPlayerName}" added successfully!`);
      setNewPlayerName('');
      setShowAddPlayerModal(false);
    } catch (error) {
      console.error("Error adding player:", error);
      setMessage(`Error adding player: ${error.message}`);
    }
  };

  // Elo rating calculation function
  const calculateElo = (playerA_score, playerB_score, isWinnerA) => {
    const RA = playerA_score;
    const RB = playerB_score;

    const QA = Math.pow(10, RA / 400);
    const QB = Math.pow(10, RB / 400);

    const EA = QA / (QA + QB);
    const EB = QB / (QA + QB);

    let newRA, newRB;

    if (isWinnerA) {
      newRA = RA + K_FACTOR * (1 - EA);
      newRB = RB + K_FACTOR * (0 - EB);
    } else {
      newRA = RA + K_FACTOR * (0 - EA);
      newRB = RB + K_FACTOR * (1 - EB);
    }

    return { newRA: Math.round(newRA), newRB: Math.round(newRB) };
  };

  // Function to record a game result
  const recordGame = async () => {
    if (!db || !userId) {
      setMessage("Database not ready or not authenticated.");
      return;
    }
    if (team1Players.length === 0 || team2Players.length === 0 || !winner) {
      setMessage("Please select players for both teams and a winner.");
      return;
    }
    if (team1Players.some(p => team2Players.includes(p)) || team2Players.some(p => team1Players.includes(p))) {
        setMessage("A player cannot be on both teams.");
        return;
    }
    if (new Set([...team1Players, ...team2Players]).size !== team1Players.length + team2Players.length) {
        setMessage("A player cannot be selected multiple times within the same game.");
        return;
    }

    try {
      // Fetch current scores for all participating players
      const allPlayerIds = [...team1Players, ...team2Players];
      const playerScoresMap = new Map();
      for (const playerId of allPlayerIds) {
        const playerDocRef = doc(db, `artifacts/${__app_id}/public/data/players`, playerId);
        const playerSnap = await getDoc(playerDocRef);
        if (playerSnap.exists()) {
          playerScoresMap.set(playerId, playerSnap.data().score);
        } else {
          setMessage(`Player with ID ${playerId} not found.`);
          return;
        }
      }

      // Calculate average scores for each team
      const team1AvgScore = team1Players.length > 0
        ? team1Players.reduce((sum, id) => sum + playerScoresMap.get(id), 0) / team1Players.length
        : INITIAL_SCORE;
      const team2AvgScore = team2Players.length > 0
        ? team2Players.reduce((sum, id) => sum + playerScoresMap.get(id), 0) / team2Players.length
        : INITIAL_SCORE;

      const isTeam1Winner = winner === 'team1';
      const { newRA: newTeam1AvgScore, newRB: newTeam2AvgScore } = calculateElo(
        team1AvgScore,
        team2AvgScore,
        isTeam1Winner
      );

      // Distribute score changes back to individual players
      const updatedPlayerScores = new Map();
      for (const playerId of allPlayerIds) {
        const currentScore = playerScoresMap.get(playerId);
        let newScore;

        if (team1Players.includes(playerId)) { // Player is on Team 1
          const scoreChange = newTeam1AvgScore - team1AvgScore;
          newScore = currentScore + scoreChange;
        } else { // Player is on Team 2
          const scoreChange = newTeam2AvgScore - team2AvgScore;
          newScore = currentScore + scoreChange;
        }
        updatedPlayerScores.set(playerId, Math.max(0, Math.round(newScore))); // Ensure score doesn't go below 0
      }

      // Update player scores in Firestore
      const batch = [];
      for (const [playerId, score] of updatedPlayerScores.entries()) {
        const playerDocRef = doc(db, `artifacts/${__app_id}/public/data/players`, playerId);
        batch.push(updateDoc(playerDocRef, { score }));
      }
      await Promise.all(batch); // Execute all updates

      // Record the game in the 'games' collection
      const gamesCollectionRef = collection(db, `artifacts/${__app_id}/public/data/games`);
      await addDoc(gamesCollectionRef, {
        team1Players: team1Players,
        team2Players: team2Players,
        winningTeam: winner,
        timestamp: new Date(),
      });

      setMessage("Game recorded and scores updated successfully!");
      // Reset form
      setTeam1Players([]);
      setTeam2Players([]);
      setWinner('');
      setShowRecordGameModal(false);
    } catch (error) {
      console.error("Error recording game:", error);
      setMessage(`Error recording game: ${error.message}`);
    }
  };

  // Helper to toggle player selection for teams
  const togglePlayerSelection = (playerId, team) => {
    if (team === 'team1') {
      if (team1Players.includes(playerId)) {
        setTeam1Players(team1Players.filter(id => id !== playerId));
      } else {
        if (team2Players.includes(playerId)) {
            setMessage("Player is already on Team 2.");
            return;
        }
        setTeam1Players([...team1Players, playerId]);
      }
    } else { // team === 'team2'
      if (team2Players.includes(playerId)) {
        setTeam2Players(team2Players.filter(id => id !== playerId));
      } else {
        if (team1Players.includes(playerId)) {
            setMessage("Player is already on Team 1.");
            return;
        }
        setTeam2Players([...team2Players, playerId]);
      }
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-100 dark:bg-gray-900 text-gray-800 dark:text-gray-200">
        <div className="text-xl font-semibold">Loading Foosball App...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-200 dark:from-gray-900 dark:to-gray-800 text-gray-800 dark:text-gray-200 p-4 font-inter">
      <div className="max-w-4xl mx-auto bg-white dark:bg-gray-850 shadow-lg rounded-xl p-6 md:p-8">
        <h1 className="text-4xl font-extrabold text-center text-blue-700 dark:text-blue-400 mb-8 drop-shadow-md">
          Foosball Score Tracker
        </h1>

        {userId && (
          <div className="text-center text-sm mb-4 text-gray-600 dark:text-gray-400">
            Your User ID: <span className="font-mono bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded-md text-xs break-all">{userId}</span>
          </div>
        )}

        {message && (
          <div className="bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 p-3 rounded-lg mb-4 text-center border border-blue-200 dark:border-blue-700">
            {message}
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          {/* Player Scores Section */}
          <div className="bg-gray-50 dark:bg-gray-800 p-6 rounded-lg shadow-inner border border-gray-200 dark:border-gray-700">
            <h2 className="text-2xl font-bold text-gray-700 dark:text-gray-300 mb-4 flex items-center">
              <svg className="w-6 h-6 mr-2 text-green-500" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path fillRule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clipRule="evenodd"></path></svg>
              Player Scores
            </h2>
            <div className="h-64 overflow-y-auto pr-2">
              {players.length === 0 ? (
                <p className="text-gray-500 dark:text-gray-400">No players added yet. Add some players to get started!</p>
              ) : (
                <ul className="space-y-2">
                  {players.map(player => (
                    <li key={player.id} className="flex justify-between items-center bg-white dark:bg-gray-700 p-3 rounded-md shadow-sm border border-gray-100 dark:border-gray-600">
                      <span className="font-medium text-gray-900 dark:text-gray-100">{player.name}</span>
                      <span className="font-bold text-lg text-purple-600 dark:text-purple-400">{player.score}</span>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>

          {/* Actions Section */}
          <div className="bg-gray-50 dark:bg-gray-800 p-6 rounded-lg shadow-inner border border-gray-200 dark:border-gray-700 flex flex-col justify-between">
            <div>
              <h2 className="text-2xl font-bold text-gray-700 dark:text-gray-300 mb-4 flex items-center">
                <svg className="w-6 h-6 mr-2 text-yellow-500" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path d="M11 3a1 1 0 100 2h2a1 1 0 100-2h-2z"></path><path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-13a1 1 0 10-2 0v2H7a1 1 0 100 2h2v2a1 1 0 102 0v-2h2a1 1 0 100-2h-2V5z" clipRule="evenodd"></path></svg>
                Actions
              </h2>
              <button
                onClick={() => setShowAddPlayerModal(true)}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-4 rounded-lg shadow-md transition duration-300 ease-in-out transform hover:scale-105 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-75 mb-4"
              >
                Add New Player
              </button>
              <button
                onClick={() => setShowRecordGameModal(true)}
                className="w-full bg-green-600 hover:bg-green-700 text-white font-bold py-3 px-4 rounded-lg shadow-md transition duration-300 ease-in-out transform hover:scale-105 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-opacity-75"
              >
                Record New Game
              </button>
            </div>
            {/* Optional: Dark mode toggle or other settings */}
            {/* <div className="mt-6 text-center text-gray-500 dark:text-gray-400 text-sm">
              <p>Built with React & Firebase</p>
            </div> */}
          </div>
        </div>
      </div>

      {/* Add Player Modal */}
      {showAddPlayerModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl p-6 w-full max-w-md transform transition-all duration-300 scale-100 opacity-100">
            <h3 className="text-2xl font-bold text-gray-800 dark:text-gray-200 mb-4">Add New Player</h3>
            <input
              type="text"
              className="w-full p-3 border border-gray-300 dark:border-gray-600 rounded-md focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-gray-100 mb-4"
              placeholder="Enter player name"
              value={newPlayerName}
              onChange={(e) => setNewPlayerName(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && addPlayer()}
            />
            <div className="flex justify-end space-x-3">
              <button
                onClick={() => setShowAddPlayerModal(false)}
                className="bg-gray-300 hover:bg-gray-400 text-gray-800 font-bold py-2 px-4 rounded-lg transition duration-200"
              >
                Cancel
              </button>
              <button
                onClick={addPlayer}
                className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-lg transition duration-200"
              >
                Add Player
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Record Game Modal */}
      {showRecordGameModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl p-6 w-full max-w-2xl transform transition-all duration-300 scale-100 opacity-100">
            <h3 className="text-2xl font-bold text-gray-800 dark:text-gray-200 mb-4">Record New Game</h3>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
              {/* Team 1 Selection */}
              <div>
                <h4 className="text-xl font-semibold text-gray-700 dark:text-gray-300 mb-3">Team 1</h4>
                <div className="space-y-2 h-48 overflow-y-auto pr-2 border border-gray-200 dark:border-gray-700 rounded-md p-2">
                  {players.map(player => (
                    <div key={`t1-${player.id}`} className="flex items-center">
                      <input
                        type="checkbox"
                        id={`t1-${player.id}`}
                        checked={team1Players.includes(player.id)}
                        onChange={() => togglePlayerSelection(player.id, 'team1')}
                        className="form-checkbox h-5 w-5 text-blue-600 rounded focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600"
                      />
                      <label htmlFor={`t1-${player.id}`} className="ml-2 text-gray-700 dark:text-gray-300 cursor-pointer">
                        {player.name}
                      </label>
                    </div>
                  ))}
                </div>
                <div className="mt-2 text-gray-600 dark:text-gray-400 text-sm">
                  Selected: {team1Players.map(id => players.find(p => p.id === id)?.name).join(', ') || 'None'}
                </div>
              </div>

              {/* Team 2 Selection */}
              <div>
                <h4 className="text-xl font-semibold text-gray-700 dark:text-gray-300 mb-3">Team 2</h4>
                <div className="space-y-2 h-48 overflow-y-auto pr-2 border border-gray-200 dark:border-gray-700 rounded-md p-2">
                  {players.map(player => (
                    <div key={`t2-${player.id}`} className="flex items-center">
                      <input
                        type="checkbox"
                        id={`t2-${player.id}`}
                        checked={team2Players.includes(player.id)}
                        onChange={() => togglePlayerSelection(player.id, 'team2')}
                        className="form-checkbox h-5 w-5 text-green-600 rounded focus:ring-green-500 dark:bg-gray-700 dark:border-gray-600"
                      />
                      <label htmlFor={`t2-${player.id}`} className="ml-2 text-gray-700 dark:text-gray-300 cursor-pointer">
                        {player.name}
                      </label>
                    </div>
                  ))}
                </div>
                <div className="mt-2 text-gray-600 dark:text-gray-400 text-sm">
                  Selected: {team2Players.map(id => players.find(p => p.id === id)?.name).join(', ') || 'None'}
                </div>
              </div>
            </div>

            {/* Winner Selection */}
            <div className="mb-6">
              <h4 className="text-xl font-semibold text-gray-700 dark:text-gray-300 mb-3">Winning Team</h4>
              <div className="flex space-x-4">
                <label className="flex items-center cursor-pointer">
                  <input
                    type="radio"
                    name="winner"
                    value="team1"
                    checked={winner === 'team1'}
                    onChange={() => setWinner('team1')}
                    className="form-radio h-5 w-5 text-blue-600 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600"
                  />
                  <span className="ml-2 text-gray-700 dark:text-gray-300">Team 1 Won</span>
                </label>
                <label className="flex items-center cursor-pointer">
                  <input
                    type="radio"
                    name="winner"
                    value="team2"
                    checked={winner === 'team2'}
                    onChange={() => setWinner('team2')}
                    className="form-radio h-5 w-5 text-green-600 focus:ring-green-500 dark:bg-gray-700 dark:border-gray-600"
                  />
                  <span className="ml-2 text-gray-700 dark:text-gray-300">Team 2 Won</span>
                </label>
              </div>
            </div>

            <div className="flex justify-end space-x-3">
              <button
                onClick={() => setShowRecordGameModal(false)}
                className="bg-gray-300 hover:bg-gray-400 text-gray-800 font-bold py-2 px-4 rounded-lg transition duration-200"
              >
                Cancel
              </button>
              <button
                onClick={recordGame}
                className="bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded-lg transition duration-200"
              >
                Record Game
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default App;
