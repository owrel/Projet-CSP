% The Social Golfer Problem
% Parameters
int: W; % The number of weeks
int: G; % The number of groups
int: P; % The number of golfers per group

int: Q = G * P;
set of int: Golfers = 0..Q-1;
set of int: Weeks = 0..W-1;
set of int: Groups = 0..G-1;
array[Weeks, Groups] of var set of Golfers: S;

constraint forall(w in Weeks, g in Groups) (
    card(S[w,g]) = P
);

constraint forall(w in Weeks) (
    card(array_union([S[w,g] | g in Groups])) = Q

);

constraint forall(q1, q2 in Golfers where q1 < q2) (
    sum(w in Weeks, g in Groups)(min(P, card(S[w, g] symdiff {q1, q2}))) >= G * P * W -2
);

solve satisfy;
