# hkpyo

Python library for handling Description Logics specifications in HK.

# Specification

Currently, the library implements a simple API for specifying description logics (DL) theories in HK. Currently, the API supports specification of:

- Concepts;
- Properties (i.e. roles);
- Individuals;
- Concept intersection;
- Concept union;
- Full universal quantification;
- Full existential quantification;
- Concept negation;
- Literals (i.e. numbers and strings).

This amounts to a ALCUE(D) DL. 

Furthermore, the API allows the specification of contextualized theories, including contextualized concepts, properties, individuals, axioms and assertions.

## Contexts

DL theories are specified in contexts. Contexts are formed by axioms, assertions and (sub) contexts, of which there are four types:

- Subconcept axiom;
- Equivalent concept axiom;
- Concept assertion axioms;
- Property assertion axioms;
- Context import axiom.

Also, named elements in a context can be refered in another context. 

There are two types of relationships between contexts, with specific semantics:

- Context inclusion: contexts might have super (parent) and sub (children) contexts. These are structural relationships: every element that is asserted in a child context is also asserted in its parent context. This is akin to the extensional interpreation of the notion of subgraph. Querying a parent context should return anything that is in its children contexts.

- Context importation: contexts might import others. This relationship is represented by an import assertion between two contexts. The informal interpreation is that any axiom or assertion valid in the imported context is valid (but not necessarily asserted) in the importing context. From a logical point of view, reasoning in the importing context should take into account axioms and assertions present in the imported context.

Reasoning in a context should then take into account elements asserted in its children contexts as well as elements asserted in imported contexts.
