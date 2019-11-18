import queue
import datetime
from message import Message
from reply import Reply
from secure_channel import SecureChannel
from control import Control


class Device(object):
	
	def __init__(self, address: int, use_crc: bool, use_secure_channel: bool):
		self._use_secure_channel = use_secure_channel
		this.address = address
		self.message_control = Control(0, use_crc, use_secure_channel)

		self._commands = queue.Queue()
		self._secure_channel = SecureChannel()
		self._last_valid_reply = datetime.datetime.now()

	@property
	def is_security_established(self) -> bool:
		return self.message_control.has_security_control_block and self._secureChannel.is_established

	@property
	def is_online(self) -> bool:
		return self._last_valid_reply + datetime.timedelta(seconds=5) >= datetime.datetime.now()

	def get_next_command_data(self) -> Command:
		if self.message_control.sequence==0:
			return PollCommand(self.address)

		if self._use_secure_channel && !self._secure_channel.is_initialized:
			return SecurityInitializationRequestCommand(self.address, self._secure_channel.serverRandomNumber)

		if self._use_secure_channel && !self._secure_channel.is_established:
			return ServerCryptogramCommand(self.address, self._secure_channel.serverCryptogram)

		if self._commands.empty():
			return PollCommand(self.address)
		else:
			command = self._commands.get(False)
			return command

	def send_command(self, command: Command):
		self._commands.put(command)

	def valid_reply_has_been_received(self, sequence: int):
		self.message_control.increment_sequence(sequence)
		self._last_valid_reply = datetime.datetime.now()

	def initialize_secure_channel(self, reply: Reply):
		reply_data = reply.extract_reply_data
		_secureChannel.initialize(reply_data[:8], reply_data[8:16], reply_data[16:32])

	def validate_secure_channel_establishment(self, reply: Reply) -> bool:
		if !reply.secure_cryptogram_has_been_accepted():
			return False

		_secureChannel.establish(reply.extract_reply_data);
		return True

	def generate_mac(self, message: bytes, is_command: bool):
		return self._secure_channel.generate_mac(message, is_command)

	def reset_security(self):
		self._secure_channel.reset()

	def encrypt_data(self, data: bytes):
		return self._secure_channel.encrypt_data(data)

	def decrypt_data(self, data: bytes):
		return self._secure_channel.decrypt_data(data)