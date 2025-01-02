% The Social Golfer Problem with Global Constraints
include "globals.mzn";

% Parameters
int: W;  % The number of weeks
int: G;  % The number of groups
int: P;  % The number of golfers per group
int: Q = G * P;  % The number of golfers

% Variables
array[1..W, 1..G, 1..P] of var 0..Q-1: schedule;
% schedule[w,g,p] représente le pème golfeur du groupe g dans la semaine w

% Constraints
constraint forall(w in 1..W) (
   alldifferent([schedule[w,g,p] | g in 1..G, p in 1..P])
);

constraint forall(k1, k2 in 0..Q-1 where k1 < k2) (
   count([schedule[w,g,p1] = k1 /\ schedule[w,g,p2] = k2 | 
          w in 1..W, g in 1..G, p1,p2 in 1..P where p1 < p2]) <= 1
);

% Contrainte de symmétrie: ordre des golfeurs dans chaque groupe
constraint forall(w in 1..W, g in 1..G, p in 1..P-1) (
   schedule[w,g,p] < schedule[w,g,p+1]
);

% Solve
solve satisfy;

% Output
output [
   "Week " ++ show(w) ++ ":\n" ++
   join(" | ", [
       show([schedule[w,g,p] | p in 1..P])
       | g in 1..G
   ]) ++ "\n"
   | w in 1..W
];