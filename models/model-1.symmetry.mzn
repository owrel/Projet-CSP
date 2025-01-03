% Parameters
int: G; % The number of groups
int: P; % The number of golfers per group
int: W; % The number of weeks

int: Q = G * P; 
int: T = W * G; 
set of int: Golfers = 0..Q-1;
set of int: Weeks = 0..W-1;
set of int: Groups = 0..G-1;
array[Weeks, Groups] of var set of Golfers: S;

constraint forall(w in Weeks, g in Groups) (
    card(S[w,g]) = P
);

constraint forall(w in Weeks, k in Golfers) (
    card({g | g in Groups where k in S[w,g]}) = 1
);

constraint forall(w1, w2 in Weeks where w1 <= w2) (
    forall(g1 in Groups, g2 in Groups where w1 == w2 -> g1 < g2) (
        card(S[w1,g1] intersect S[w2,g2]) <= 1
    )
);


% C_4 : Premiére semaine
constraint forall(g in Groups) (
    forall(i in 0..P-1) (
        S[0, g] = S[0, g] union {g*P + i}
    )
);

% C_5 : Ordonnancement des groupes par minimum
constraint forall(w in Weeks) (
   forall(g1, g2 in Groups where g1 < g2) (
       min(S[w,g1]) < min(S[w,g2])
   )
);

%C_6: Ordre croissant des maximums dans le premier groupe
constraint forall(w1, w2 in Weeks where w1 < w2) (
    max(S[w1,0]) <= max(S[w2,0]) 
);

solve satisfy;


