% Parameters
#const weeks = 5.
#const groups = 3.
#const players_per_group = 2.
#const players = groups * players_per_group.

% Generate: assign players to groups in each week
1 { assigned(W,G,P) : group(G) } 1 :- week(W), player(P).

% Domain definitions
week(0..weeks-1).
group(0..groups-1).
player(0..players-1).

% Each group must have exactly players_per_group players
:- group(G), week(W), not players_per_group = #count{ P : assigned(W,G,P) }.

% Players cannot be in multiple groups in the same week
:- assigned(W,G1,P), assigned(W,G2,P), G1 != G2.

% Players cannot meet more than once across weeks (relaxed version)
:- assigned(W1,G1,P1), assigned(W1,G1,P2),
   assigned(W2,G2,P1), assigned(W2,G2,P2),
   P1 < P2, W1 < W2.

% Optional: output formatting
#show assigned/3.
