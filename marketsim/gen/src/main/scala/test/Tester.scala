package test

object Tester {

    def main(args : Array[String])
    {
        val tests =
            Scheduler ::
            OrderMatching ::
            ChunkDeque ::
            LocalOrderBook ::
            Link ::
            RemoteOrderBook ::
            order.ImmediateOrCancel ::
            order.WithExpiry ::
            order.Iceberg ::
                    Nil

        tests foreach { t =>
            var result = List.empty[String]
            t({ s => { result = s :: result }})
            scala.tools.nsc.io.File(s"test_result/${t.productPrefix}.result").writeAll(result.reverse mkString "\n")
        }

    }

}
