module Fitgem
  class Client
    API_VERSION = '1'
    EMPTY_BODY = ''

    def authorize(token, secret, opts={})
      request_token = OAuth::RequestToken.new(consumer, token, secret)
      @access_token = request_token.get_access_token(opts)
      @token = @access_token.token
      @secret = @access_token.secret
      @access_token
    end

    # Get an authentication request token
    #
    # @param [Hash] opts Additional request token request data
    # @return [OAuth::RequestToken]
    def authentication_request_token(opts={})
      consumer.options[:authorize_path] = '/oauth/authenticate'
      request_token(opts)
    end
    private

      def consumer
        @consumer ||= OAuth::Consumer.new(@consumer_key, @consumer_secret, {
          :site => 'https://api.fitbit.com',
          :authorize_url => 'https://www.fitbit.com/oauth/authorize',
          :proxy => @proxy
        })
      end
  end
end