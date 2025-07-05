public class FitbitShim extends OAuth1ShimBase {

    public static final String SHIM_KEY = "fitbit";

    private static final String DATA_URL = "https://api.fitbit.com";

    private static final String REQUEST_TOKEN_URL = "https://api.fitbit.com/oauth/request_token";

    private static final String AUTHORIZE_URL = "https://www.fitbit.com/oauth/authenticate";

    private static final String TOKEN_URL = "https://api.fitbit.com/oauth/access_token";

    @Value("${openmhealth.shim.fitbit.partnerAccess:false}")
    protected boolean partnerAccess;

    @Autowired
    public FitbitShim(ApplicationAccessParametersRepo applicationParametersRepo,
            AuthorizationRequestParametersRepo authorizationRequestParametersRepo,
            ShimServerConfig shimServerConfig,
            AccessParametersRepo accessParametersRepo) {
        super(applicationParametersRepo, authorizationRequestParametersRepo, shimServerConfig, accessParametersRepo);
    }

    @Override
    public String getShimKey() {
        return SHIM_KEY;
    }

    @Override
    public String getBaseRequestTokenUrl() {
        return REQUEST_TOKEN_URL;
    }
    @Override
    public String getBaseAuthorizeUrl() {
        return AUTHORIZE_URL;
    }

    @Override
    public String getBaseTokenUrl() {
        return TOKEN_URL;
    }
}
