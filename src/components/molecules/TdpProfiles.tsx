import { useTdpProfilesEnabled } from "../../hooks/useEnableTdpProfiles";
import { useSelector } from "react-redux";
import { getCurrentTdpInfoSelector } from "../../redux-modules/settingsSlice";
import ErrorBoundary from "../ErrorBoundary";
import { DeckyRow, DeckyToggle } from "../atoms/DeckyFrontendLib";

export function TdpProfiles({ isDesktop }: { isDesktop: boolean }) {
  const [tdpProfilesEnabled, setTdpProfilesEnabled] = useTdpProfilesEnabled();

  const { displayName } = useSelector(getCurrentTdpInfoSelector);

  const description = getDescription(
    isDesktop,
    displayName,
    tdpProfilesEnabled
  );

  const label = isDesktop
    ? "Desktop 프로파일 사용"
    : "게임별 프로파일 사용";

  return (
    <DeckyRow>
      <ErrorBoundary title="Tdp Profiles">
        <DeckyToggle
          label={label}
          checked={tdpProfilesEnabled}
          onChange={(enabled: boolean) => {
            setTdpProfilesEnabled(enabled);
          }}
          description={description}
          highlightOnFocus
        />
      </ErrorBoundary>
    </DeckyRow>
  );
}

function getDescription(
  isDesktop: boolean,
  displayName: string,
  tdpProfilesEnabled: boolean
) {
  if (tdpProfilesEnabled) {
    const formattedDisplayName = isDesktop
      ? displayName
      : displayName.substring(0, 20);

    return Boolean(displayName) && displayName.toLowerCase() !== "default"
      ? `Using - ${formattedDisplayName}...`
      : `Using - Default`;
  }
  return "";
}
