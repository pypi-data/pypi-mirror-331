import unittest

from foxglove import Schema
from foxglove.channel import Channel
from foxglove.channels import LogChannel
from foxglove.schemas import Log


class TestChannel(unittest.TestCase):
    topic: str

    def setUp(self) -> None:
        self.topic = unittest.TestCase.id(self)

    def test_prohibits_duplicate_topics(self) -> None:
        schema = {"type": "object"}
        _ = Channel("test-duplicate", schema=schema)
        self.assertRaisesRegex(
            ValueError, "already exists", Channel, "test-duplicate", schema=schema
        )

    def test_requires_an_object_schema(self) -> None:
        schema = {"type": "array"}
        self.assertRaisesRegex(
            ValueError,
            "Only object schemas are supported",
            Channel,
            self.topic,
            schema=schema,
        )

    def test_log_dict_on_json_channel(self) -> None:
        channel = Channel(
            self.topic,
            schema={"type": "object", "additionalProperties": True},
        )
        self.assertEqual(channel.message_encoding, "json")

        channel.log({"test": "test"})

    def test_log_must_serialize_on_protobuf_channel(self) -> None:
        channel = Channel(
            self.topic,
            message_encoding="protobuf",
            schema=Schema(
                name="my_schema",
                encoding="protobuf",
                data=b"\x01",
            ),
        )

        self.assertRaisesRegex(
            ValueError, "Unsupported message type", channel.log, {"test": "test"}
        )
        channel.log(b"\x01")

    def test_closed_channel_log(self) -> None:
        channel = Channel(self.topic, schema={"type": "object"})
        channel.close()
        with self.assertLogs("foxglove.channels", level="DEBUG") as logs:
            channel.log(b"\x01")
            self.assertRegex(logs.output[0], "Cannot log\\(\\) on a closed channel")

    def test_close_typed_channel(self) -> None:
        channel = LogChannel("/topic")
        channel.close()
        with self.assertLogs("foxglove.channels", level="DEBUG") as logs:
            channel.log(Log())
            self.assertRegex(logs.output[0], "Cannot log\\(\\) on a closed LogChannel")


if __name__ == "__main__":
    unittest.main()
