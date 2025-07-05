#Used by Subtype: USER
sub fitbit_getSleepGoals($) {
  my ($hash) = @_;
  my $name = $hash->{NAME};
  my $userID = $hash->{USERID};

  Log3 $name, 4, "$name: fitbit_getSleepGoals() ".$hash->{USERID};
  return undef if( !defined($hash->{IODev}) );

  my $token = fitbit_decrypt( $hash->{IODev}->{helper}{token} );
  Log3 $name, 5, "$name: fitbit_getSleepGoals(): Use token from I/O Dev $hash->{IODev}->{NAME}";

  my $now = substr(TimeNow(),0,10);
  HttpUtils_NonblockingGet({
    url => "https://api.fitbit.com/1/user/-/sleep/goal.json",
    timeout => 30,
    noshutdown => 1,
    header => {"Authorization" => 'Bearer '. $token, "Accept-Locale" => 'de_DE'},
    hash => $hash,
    type => 'sleepGoals',
    callback => \&fitbit_Dispatch,
  });

  $hash->{LAST_POLL} = TimeNow();
  readingsSingleUpdate( $hash, ".poll", gettimeofday(), 0 );
  return undef;
}
