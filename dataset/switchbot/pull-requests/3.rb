module Switchbot
	class Client
	  API_ENDPOINT = 'https://api.switch-bot.com'
  
	  def initialize(token)
		@token = token
	  end
  
	  def devices
		request(
		  http_method: :get,
		  endpoint: 'v1.0/devices'
		)
	  end

	  def device(device_id)
		Device.new(client: self, device_id: device_id)
	  end
	  def status(device_id:)
		request(
		  http_method: :get,
		  endpoint: "/v1.0/devices/#{device_id}/status"
		)
	  end
  
	  def commands(device_id:, command:, parameter: 'default', command_type: 'command')
		request(
		  http_method: :post,
		  endpoint: "/v1.0/devices/#{device_id}/commands",
		  params: {
			command: command,
			parameter: parameter,
			commandType: command_type
		  }
		)
	  end
	  def scenes
		request(
		  http_method: :get,
		  endpoint: 'v1.0/scenes'
		)
	  end

	  def scene(scene_id)
		Scene.new(client: self, scene_id: scene_id)
	  end
	  def execute(scene_id:)
		request(
		  http_method: :post,
		  endpoint: "/v1.0/scenes/#{scene_id}/execute"
		)
	  end

	  private
  
	  def headers
		{
		  'User-Agent' => "Switchbot v#{Switchbot::VERSION} (https://github.com/ytkg/switchbot)",
		  'Authorization' => @token
		}
	  end

	  def request(http_method:, endpoint:, params: {})
		response = connection.public_send(http_method, endpoint, params)
		response.body.deep_transform_keys(&:underscore).deep_symbolize_keys
	  end
	end
end
