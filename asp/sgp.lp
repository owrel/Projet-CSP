#const weeks = 2.
#const groups = 3.
#const size = 3.


golfer(1..G) :- G = groups * size.
week(1..weeks).
group(1..groups).

1 { assign(P, G, W) : group(G) } 1 :- golfer(P), week(W).

:- week(W), group(G), not #count{P : assign(P,G,W)} = size.

:- golfer(X), week(W), #count{G : assign(X,G,W)} > 1.

% Social constraint: golfers can't play together more than once
:- golfer(X), golfer(Y), X < Y,
   assign(X,G1,W1), assign(Y,G1,W1),
   assign(X,G2,W2), assign(Y,G2,W2),
   W1 < W2.

#show assign/3.
