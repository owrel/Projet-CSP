% The Social Golfer Problem
% Parameters
int: W; % The number of weeks
int: G; % The number of groups
int: P; % The number of golfers per group

% Variables
int: Q = G * P; % The number of golfers
set of int: Golfers = 0..Q-1;
set of int: Weeks = 0..W-1;
set of int: Groups = 0..G-1;
array[Weeks, Groups] of var set of Golfers: S; % The schedule matrix

% Constraints
% P golfers per group
constraint forall(w in Weeks, g in Groups) (
    card(S[w,g]) = P
);

% All golfers play exactly one time in a week
constraint forall(w in Weeks) (
    card(array_union([S[w,g] | g in Groups])) = Q

);

% A golfer meets at most one time each golfer
constraint forall(q1, q2 in Golfers where q1 < q2) (
    sum(w in Weeks, g in Groups)(bool2int(q1 in S[w, g] /\ q2 in S[w, g])) <= 1
);

% Solve
solve satisfy;
