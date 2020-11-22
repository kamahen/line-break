# Implementation notes

## Dynamic programming

The paper describes the algorithm DYNAMIC but omits explaining how to
read off the result. This presentation provides a method: [A Gentle
Introduction to Dynamic Programming and the Viterbi
Algorithm](http://www.cambridge.org/resources/0521882672/7934_kaeslin_dynpro_new.pdf).
The basic idea is to label each node with the total cost to that
point, then proceed backwards from the end state, using the lowest
cost connected node at each step.


## 1-origin indexing

The algorithms in the paper use 1-origin indexing and also a
2-dimensional array for the cost values. The easiest way of
representing this in Python is as a dict.

In some cases, the arrays are represented as sparse (e.g.,the `splits`
dict that I added to record optimal split points).

## Typos in the paper

None of the typos in the paper are serious, except for one in the
LINE-BREAKER algorithm. In computing `P`, there's clearly a bug with
`P[J] := K` because `P` is indexed by line number and `J` is a word
index.

## Cost function

The cost function is defined as
`1+1/F[I,J]` if `F[I,J]` &le; `D` & `J` &lt; `N`.
However, if `F[I,J]` is 1 (a single letter word), then the cost is 2,
the same as for the first condition of the cost function:
if `F[I,J]` &le; `D` & `J` = `N`.

Perhaps the cost function should be redefined as `1+0.999/F[I,J]`, so
that the last line's cost function is always 2?

## Cost function for line breaks

The text defines the cost function for a line break as `1+min(C[I,K] *
C[K+1,J], I &le; K &lt; J)` but in the code it seems to be
`min(C[I,K] * C[K+1,J], I &le; K &lt; J) in the code -- that is, the
constant factor `1` isn't there. I've put the `1+` into
DYNAMIC - it doesn't make any difference for LINE_BREAKER.


## DYNAMIC and optimal splits

The paper doesn't describe how to extract the optimal split points
from DYNAMIC, but implies that it's easy.

My solution is to loop backwards through the lines: for each possible
line, select the split point that minimizes the cost from the
beginning of the paragraph to the end of this line. This seems to give
the same results as LINE-BREAKER.

TODO: Better handling of multiple minimal split points. I suggest
adding a small factor to the cost function that takes into account the
number of words, not just the width of the words. This will help
reduce large blocks of white space.

## c[i] and c[i,N]

c[i] is defined as c[i,N].

## P in LINE-BREAKER

The loop at the end confuses me ... it seems to do nothing more than
shift the values to the right: `P[2:M-1] = P[1:M-2]` (The 3 lines
inside the loop are equivalent to `P[I],J:=J,P[I]` which simplifies to
`P[I]:=P[I-1]`).  (P[1] and P[M] are, of course, special -- P[1] must
always be 1 and P[M] should always be S[M] (shortest possible last
line)). But the question remains: why not just store the value in
P[I+1] instead of P[I] (and separately set P[1], P[M])?
