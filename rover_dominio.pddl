;Header and description

(define (domain rover_domain)

(:requirements :strips :typing)
  (:types rover localidad mineral)

  (:predicates
    (en ?r - rover ?l - localidad)
    (mineral-en ?m - mineral ?l - localidad)
    (mineral-transportado ?m - mineral)
    (camino ? from ?to - localidad) 
  )

  (:action mover
    :parameters (?r - rover ?from ?to - localidad)
    :precondition (and (en ?r ?from) (camino ?from ?to))
    :effect (and (not (en ?r ?from)) (en ?r ?to))
  )

  (:action recoger
    :parameters (?r - rovern ?m - mineral ?l - localidad)
    :precondition (and (en ?r ?l) (mineral-en ?m ?l)) 
    :effect (and (not (mineral-en ?m ?l)) (mineral-transportado ?m))
  )

  (:action entregar
    :parameters (?r - rover ?m - mineral ?l - localidad)
    :precondition (and (en ?r ?l) (mineral-transportado ?m))
    :effect (and (not (mineral-transportado ?m)) (mineral-en ?m ?l))
  )

)

  