import unittest
from unittest.mock import patch, MagicMock
from plugins.idiom import idiom  # 确保这里的路径是正确的
from bridge.context import ContextType
from bridge.reply import Reply, ReplyType
from channel.chat_message import ChatMessage
from plugins import EventAction
class TestIdiomGameFlow(unittest.TestCase):
    def setUp(self):
        # 初始化插件实例
        self.plugin = idiom()
        self.plugin.game_mode_rooms = {}
        self.plugin.game_point = {}
        self.plugin.game_answer = {}
        self.plugin.game_success = {}
        self.plugin.idiom_pic = {}
        self.plugin.current_round = {}

        # 初始化模拟的上下文和消息
        self.mock_context = {
            'type': ContextType.TEXT,
            'msg': MagicMock(),
            'content': ''
        }
        self.mock_message = MagicMock()
        self.mock_message.room_id = 'test_room_id'
        self.mock_message.from_user_id = 'test_user_id'
        self.mock_message.actual_user_nickname = 'test_nickname'

        self.mock_event_context = {
            'context': self.mock_context,
            'reply': None,
            'action': EventAction.BREAK_PASS
        }

    @patch('plugins.idiom.IdiomGame.get_idiom')
    def test_game_flow(self, mock_get_idiom):
        # 模拟获取成语数据
        mock_get_idiom.side_effect = [
            ('path/to/image1', {'答案': '成语一'}),
            ('path/to/image2', {'答案': '成语二'}),
            ('path/to/image3', {'答案': '成语三'}),
            ('path/to/image4', {'答案': '成语四'}),
            ('path/to/image5', {'答案': '成语五'})
        ]

        # 开始游戏
        self.mock_context['msg'].content = '看图猜成语'
        self.plugin.on_receive_message(self.mock_event_context)
        self.assertIn(self.mock_message.room_id, self.plugin.game_mode_rooms)
        self.assertTrue(self.plugin.game_mode_rooms[self.mock_message.room_id])

        # 模拟用户回答
        self.plugin.game_mode_rooms[self.mock_message.room_id] = True
        self.plugin.current_round[self.mock_message.room_id] = 1
        self.mock_context['msg'].content = '成语一'
        self.plugin.on_receive_message(self.mock_event_context)
        self.assertTrue(self.plugin.game_success[self.mock_message.room_id])

        # 继续游戏流程
        for round in range(2, 6):
            self.plugin.current_round[self.mock_message.room_id] = round
            self.mock_context['msg'].content = '成语' + str(round)
            self.plugin.on_receive_message(self.mock_event_context)
            self.assertTrue(self.plugin.game_success[self.mock_message.room_id])

        # 结束游戏
        self.plugin.current_round[self.mock_message.room_id] = 5
        self.mock_context['msg'].content = '成语五'
        self.plugin.on_receive_message(self.mock_event_context)
        self.assertIsNone(self.plugin.game_mode_rooms[self.mock_message.room_id])
        self.assertEqual(self.plugin.game_point[self.mock_message.room_id]['test_nickname'], 5)

    # 可以添加更多的测试用例来覆盖其他功能和边界条件

if __name__ == '__main__':
    unittest.main()