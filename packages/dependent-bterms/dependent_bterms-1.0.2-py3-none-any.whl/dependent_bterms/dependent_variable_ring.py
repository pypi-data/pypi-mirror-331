"""Construction of the modified asymptotic ring with a dependent variable.

This module contains the central interface of our package, the
:func:`.AsymptoticRingWithDependentVariable` function.

TESTS::

    sage: import dependent_bterms as dbt
    sage: AR, n, k = dbt.AsymptoticRingWithDependentVariable('n^QQ', 'k', 0, 1/2)
    sage: AR.B(k*n)
    doctest:warning
    ...
    FutureWarning: ...
    ...
    B(abs(k)*n, n >= 0)

"""

from __future__ import annotations

from sage.symbolic.ring import SR

from sage.rings.asymptotic.asymptotic_ring import AsymptoticRing, AsymptoticExpansion
from sage.rings.asymptotic.term_monoid import TermMonoidFactory
from sage.symbolic.expression import Expression

from .structures import (
    MonBoundExactTermMonoidFactory,
    MonBoundOTermMonoidFactory,
    MonBoundBTermMonoidFactory,
    AsymptoticRingWithCustomPosetKey,
)


def _add_monomial_growth_restriction_to_ring(
    AR: AsymptoticRing,
    dependent_variable: Expression,
    lower_bound: AsymptoticExpansion,
    upper_bound: AsymptoticExpansion,
    bterm_round_to: None | int = None,
) -> AsymptoticRing:
    """Helper function to modify a given asymptotic ring such
    that an additional symbolic variable bounded in a specified
    range is supported.

    ::

        sage: import dependent_bterms as dbt
        sage: A, n, k = dbt.AsymptoticRingWithDependentVariable('n^QQ', 'k', 0, 1/2)
        sage: A.B(k*n)
        B(abs(k)*n, n >= 0)
        sage: (k*n).O()
        O(n^(3/2))
    """
    lower_bound = AR(lower_bound)
    upper_bound = AR(upper_bound)
    term_monoid_factory = TermMonoidFactory(
        name=f"{__name__}.TermMonoidFactory",
        exact_term_monoid_class=MonBoundExactTermMonoidFactory(
            dependent_variable=dependent_variable,
            lower_bound=lower_bound,
            upper_bound=upper_bound,
        ),
        O_term_monoid_class=MonBoundOTermMonoidFactory(
            dependent_variable=dependent_variable,
            lower_bound=lower_bound,
            upper_bound=upper_bound,
        ),
        B_term_monoid_class=MonBoundBTermMonoidFactory(
            dependent_variable=dependent_variable,
            lower_bound=lower_bound,
            upper_bound=upper_bound,
            bterm_round_to=bterm_round_to,
        ),
    )
    return AR.change_parameter(term_monoid_factory=term_monoid_factory)


def AsymptoticRingWithDependentVariable(
    growth_group,
    dependent_variable,
    lower_bound_power,
    upper_bound_power,
    lower_bound_factor=1,
    upper_bound_factor=1,
    bterm_round_to=None,
    **ring_kwargs,
):
    """Instantiate a special (univariate) :class:`.AsymptoticRing` that
    is aware of a monomially bounded symbolic variable.

    INPUT:

    - ``growth_group`` -- the (univariate) growth group of
      the :class:`.AsymptoticRing`.

    - ``dependent_variable`` -- a string representing a variable
      in the :class:`.SymbolicRing`, or any valid input for
      :meth:`.SymbolicRing.var`.

    - ``lower_bound_power`` -- a nonnegative real number, the power
      to which the ring's independent variable is raised to in order
      to obtain the lower monomial power bound.

    - ``upper_bound_power`` -- analogous to ``lower_bound_power``, just
      for the upper bound.

    - ``lower_bound_factor`` -- a nonnegative real number, the constant
      with which the monomial power is multiplied to form the lower bound.

    - ``upper_bound_factor`` -- a nonnegative real number, the constant
      with which the monomial power is multiplied to form the upper bound.

    - ``bterm_round_to`` -- a positive integer or ``None`` (the default):
      the number of floating point digits to which the coefficients
      of B-terms are rounded.

    - ``ring_kwargs`` -- further keyword arguments being passed to
      the :class:`.AsymptoticRing` constructor.


    SEEALSO:

    - :class:`.AsymptoticRing`


    TESTS::

        sage: import dependent_bterms as dbt
        sage: A, n, k = dbt.AsymptoticRingWithDependentVariable('n^QQ', 'k', 0, 1/2)
        sage: A.term_monoid_factory.BTermMonoid
        <class 'dependent_bterms.structures.MonBoundBTermMonoidFactory.<locals>.MonBoundBTermMonoid'>
        sage: O(k*n)
        O(n^(3/2))

    Make sure that scaled monomial bounds also work as intended::

        sage: A, n, k = dbt.AsymptoticRingWithDependentVariable('n^QQ', 'k', 0, 1/2,
        ....:     upper_bound_factor=2, default_prec=5)
        sage: dbt.simplify_expansion((n*k).B(valid_from=10), simplify_bterm_growth=True)
        B(2*n^(3/2), n >= 10)

    """
    AR = AsymptoticRingWithCustomPosetKey(
        growth_group=growth_group,
        coefficient_ring=SR,
        **ring_kwargs,
    )
    k = SR.var(dependent_variable)
    n = AR.gen()
    AR_with_bound = _add_monomial_growth_restriction_to_ring(
        AR,
        k,
        lower_bound=AR(lower_bound_factor) * n**lower_bound_power,
        upper_bound=AR(upper_bound_factor) * n**upper_bound_power,
        bterm_round_to=bterm_round_to,
    )
    n = AR_with_bound.gen()
    return AR_with_bound, n, k
