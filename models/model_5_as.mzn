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


% Symmetry-breaking constraint for the first week
constraint forall(g in Groups) (
    forall(i in 0..P-1) (
        S[0, g] = S[0, g] union {g*P + i}
    )
);

% Symmetry-breaking constraint for the first player of all group after week 0
constraint forall(w in 1..W-1) (
    forall(g in Groups where g<P) (
          S[w, g] intersect {g} = {g}
    )
);

% Constraint on the order where the lowest max will always be first (only for the 1st group)
constraint forall(w1, w2 in Weeks where w1 < w2) (
    max(S[w1,0]) <= max(S[w2,0])
);

% Constraint on the order where the lowest min is always first (only for the 1st group)
constraint forall(w1, w2 in Weeks where w1 < w2 /\ P > 1) (
    min(S[w1,0] diff {0}) <= min(S[w2,0] diff {0})
);

% constraint on the order of golfers changing team except the "captains"
constraint forall(w1,w2 in Weeks, g1,g2 in 1..G-1 where g2 == g1+1 /\ P > 1 /\ w2 == w1+1) (
   card(S[w1,g1] intersect S[w2,g2]) > 0 /\
   card(S[w1,G-1] intersect S[w2,1]) > 0
);

% Solve
solve satisfy;
