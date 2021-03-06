package marketsim

import scala.collection.mutable

trait IEvent
{
    def advise (listener : () => Unit)
}

class Event[T] extends IEvent {

    var listeners = List.empty[T => Unit]

    def += (listener : T => Unit) {
        if ((listeners indexOf listener) == -1)
            listeners = listener :: listeners
    }

    def advise (listener : () => Unit) = {
        def inner(x : T) = listener()
        this += inner
    }

    def fire(x : T) {
        listeners foreach { _(x) }
    }
}

object Event
{
    def Every(interval : () => Time) =
        new IEvent {
            var listeners = List.empty[() => Unit]

            def advise (listener : () => Unit) {
                if ((listeners indexOf listener) == -1)
                    listeners = listener :: listeners
            }

            def fire() = listeners foreach { _() }

            import Scheduler.process
            process(interval, fire)
        }
}

abstract class OptObservable[T] extends Event[Option[T]] with (() => Option[T])
{
    protected var _value = Option.empty[T]

    def value = _value

    def apply() = _value

    protected def update(x : Option[T]) {
        if (x != _value) {
            _value = x
            fire(_value)
        }
    }
}

abstract class Observable[T](protected var _value : T) extends Event[T] with (() => T)
{
    def value = _value

    def apply() = _value

    protected def update(x : T) {
        if (x != _value) {
            _value = x
            fire(_value)
        }
    }
}

case class OnEveryDt_[T](dt : Time, f : () => T) extends Observable[T](f())
{
    import Scheduler.process
    process(const(dt), { () => update(f()) })

    override def toString() = s"OnEveryDt($dt, $f)"
}

object OnEveryDt
{
    private val cache = collection.mutable.HashMap.empty[Any, Any]

    def apply[T](dt : Time, f : () => T) =
        (cache getOrElseUpdate ((dt, f), new OnEveryDt_[T](dt, f))).asInstanceOf[OnEveryDt_[T]]
}

abstract class OnceConditionBase[T <% Ordered[T]](source : OptObservable[T])
{
    type Element = (T, () => Unit)

    implicit object Ord extends Ordering[Element] {
        def compare(x: Element, y: Element) =
            cmp(x._1, y._1)
    }

    def cmp(x : T, y : T) : Int

    private var handlers = collection.mutable.PriorityQueue.empty[(T, () => Unit)]

    def += (x : (T, () => Unit))
    {
        val (trigger, handler) = x
        if (source.value.nonEmpty && cmp(source.value.get, trigger) < 0)
            handler()
        else
            handlers enqueue x
    }

    def -= (x : (T, () => Unit))
    {
        handlers = (handlers partition { _ == x})._2
    }

    source += {
        case None =>
        case Some(x) =>
            while (handlers.nonEmpty && cmp(handlers.head._1, x) > 0)
                handlers.dequeue()._2()
    }
}

case class OnceGreaterThan_[T <% Ordered[T]](source : OptObservable[T]) extends OnceConditionBase[T](source)
{
    def cmp(x : T, y : T) = -(x compare y)
}

object OnceGreaterThan
{
    private val cache = mutable.HashMap.empty[Any,Any]

    def apply[T <% Ordered[T]](source : OptObservable[T]) =
        (cache getOrElseUpdate (source, new OnceGreaterThan_[T](source))).asInstanceOf[OnceGreaterThan_[T]]
}

case class OnceLessThan_[T <% Ordered[T]](source : OptObservable[T]) extends OnceConditionBase[T](source)
{
    def cmp(x : T, y : T) = +(x compare y)
}

object OnceLessThan
{
    private val cache = mutable.HashMap.empty[Any,Any]

    def apply[T <% Ordered[T]](source : OptObservable[T]) =
        (cache getOrElseUpdate (source, new OnceLessThan_[T](source))).asInstanceOf[OnceLessThan_[T]]
}
