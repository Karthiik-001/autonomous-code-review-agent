import { useState } from "react";

type UserDataButtonProps = {
  url?: string;
};

type User = {
  name: string;
};

function UserDataButton({ url = "/api/user" }: UserDataButtonProps) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadUser = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch(url);
      const nextUser = (await response.json()) as User;
      setUser(nextUser);
    } catch {
      setError("Could not load user data. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div>
      <button type="button" onClick={loadUser} disabled={isLoading}>
        {isLoading ? "Loading..." : "Load user"}
      </button>
      {user && <p>{user.name}</p>}
      {error && <p role="alert">{error}</p>}
    </div>
  );
}

export default UserDataButton;
