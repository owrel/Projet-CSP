% The Social Golfer Problem

% Parameters
int: G; % The number of groups
int: P; % The number of golfers per group
int: W = 3; % The number of weeks

% Variables
int: Q = G * P; % The number of golfers
int: T = W * G; % The number of matches
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
constraint forall(w1, w2 in Weeks where w1 <= w2) (
    forall(g1 in Groups, g2 in Groups where w1 == w2 -> g1 < g2) (
        card(S[w1,g1] intersect S[w2,g2]) <= 1
    )
);

% Solve
solve satisfy;

% Output
% output [
%      show(S[w,g])++" | "++ if g==G-1 then "\n" endif | w in Weeks, g in Groups
% ];